"""DreamFactory File Storage Operations Tools."""

import base64
import json
from typing import Annotated

from arcade_tdk import ToolContext, tool
from arcade_tdk.errors import RetryableToolError, ToolExecutionError
from loguru import logger

from .utils import (
    format_response,
    get_dreamfactory_config,
    make_dreamfactory_request,
)


def is_binary_content(content: str) -> bool:
    """Check if content appears to be binary data."""
    try:
        content.encode('utf-8')
        # Check for null bytes or other control characters
        return '\x00' in content or any(ord(c) < 32 and c not in '\t\n\r' for c in content[:100])
    except (UnicodeDecodeError, UnicodeEncodeError):
        return True


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_storage_services(
    context: ToolContext
) -> str:
    """List all configured file storage services.

    Returns available storage services like local file storage, S3, Azure Blob, etc.
    Use this to see what storage services are available before file operations.

    Examples:
        list_storage_services()
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Get all services and filter for file storage types
    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/service",
        headers=headers
    )

    # Filter for storage service types
    storage_types = ["local", "s3", "azure", "ftp", "sftp", "webdav", "rackspace", "openstack"]
    storage_services = []

    for service in response.get("resource", []):
        if any(storage_type in service.get("type", "").lower() for storage_type in storage_types):
            storage_services.append({
                "id": service.get("id"),
                "name": service.get("name"),
                "type": service.get("type"),
                "description": service.get("description", ""),
                "is_active": service.get("is_active", False)
            })

    logger.info(f"Found {len(storage_services)} storage services")

    return format_response({
        "storage_services": storage_services,
        "count": len(storage_services)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_files(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service (e.g., 'local', 's3_bucket')"],
    path: Annotated[str, "Directory path to list (use '/' for root, 'folder/' for subfolder)"] = "/",
    recursive: Annotated[bool, "Include files from subdirectories"] = False,
    include_folders: Annotated[bool, "Include folders in the listing"] = True,
    pattern: Annotated[str, "File pattern to match (e.g., '*.txt', '*.pdf')"] = "",
    search_term: Annotated[str, "Search for files by name (case-insensitive partial match)"] = ""
) -> str:
    """List and search files and folders in a storage service.

    Use this to explore and search the contents of file storage services.
    Supports local storage, S3, Azure Blob, FTP, SFTP, and WebDAV.

    Examples:
        List root: list_files("local", "/")
        List subfolder: list_files("s3_bucket", "documents/")
        List recursively: list_files("local", "/data", recursive=True)
        Filter by pattern: list_files("local", "/logs", pattern="*.log")
        Search by name: list_files("local", "/", search_term="report", recursive=True)
        Combined: list_files("local", "/data", pattern="*.csv", search_term="sales")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Ensure path ends with / for directories
    if path and not path.endswith("/") and not pattern:
        path = path + "/"

    # Build query parameters
    params = {}
    if recursive:
        params["recursive"] = "true"
    if not include_folders:
        params["include_folders"] = "false"
    if pattern:
        params["pattern"] = pattern

    # Clean up path - remove leading slash for non-root paths
    if path != "/" and path.startswith("/"):
        path = path[1:]

    url = f"{config['base_url']}/{storage_service}"
    if path and path != "/":
        url = f"{url}/{path}"

    response = make_dreamfactory_request(
        method="GET",
        url=url,
        headers=headers,
        params=params
    )

    # Extract file/folder information
    items = response.get("resource", [])
    files = []
    folders = []

    # Apply search term filter if provided
    search_lower = search_term.lower() if search_term else ""

    for item in items:
        # Check if item matches search term (if provided)
        item_name = item.get("name", "")
        if search_term and search_lower not in item_name.lower():
            continue

        item_info = {
            "name": item_name,
            "path": item.get("path"),
            "size": item.get("content_length", 0),
            "modified": item.get("last_modified"),
            "type": item.get("content_type", "")
        }

        if item.get("type") == "folder":
            folders.append(item_info)
        else:
            files.append(item_info)

    result = {
        "storage_service": storage_service,
        "path": path,
        "files": files,
        "file_count": len(files)
    }

    if search_term:
        result["search_term"] = search_term

    if include_folders:
        result["folders"] = folders
        result["folder_count"] = len(folders)

    log_msg = f"Listed {len(files)} files and {len(folders)} folders in {storage_service}:{path}"
    if search_term:
        log_msg += f" matching '{search_term}'"
    logger.info(log_msg)

    return format_response(result)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def read_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    file_path: Annotated[str, "Full path to the file (e.g., 'documents/report.txt')"],
    as_base64: Annotated[bool, "Return binary files as base64 encoded string"] = False,
    metadata_only: Annotated[bool, "Return only file metadata without content"] = False
) -> str:
    """Read file contents or metadata from a storage service.

    Returns text content, binary content as base64, or just metadata information.
    Automatically detects binary files and encodes them when needed.

    Examples:
        Text file: read_file("local", "config/settings.json")
        Binary file: read_file("s3_bucket", "images/logo.png", as_base64=True)
        Metadata only: read_file("local", "large_file.zip", metadata_only=True)
        From subfolder: read_file("local", "data/exports/report.csv")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # Add parameter to get content (unless metadata_only)
    params = {"include_content": "false" if metadata_only else "true"}

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{storage_service}/{file_path}",
        headers=headers,
        params=params
    )

    # Build result with metadata
    result = {
        "storage_service": storage_service,
        "file_path": file_path,
        "name": response.get("name"),
        "content_type": response.get("content_type", "text/plain"),
        "size": response.get("content_length", 0),
        "modified": response.get("last_modified"),
        "created": response.get("created_date")
    }

    if metadata_only:
        result["metadata"] = response.get("metadata", {})
        logger.info(f"Read metadata for {storage_service}:{file_path}")
    else:
        # Extract content
        content = response.get("content", "")
        content_type = response.get("content_type", "text/plain")

        # Check if content is already base64 encoded (DreamFactory does this for binary files)
        is_binary = "image" in content_type or "application" in content_type or is_binary_content(str(content))

        if is_binary and not as_base64:
            result["content"] = "[Binary content - use as_base64=True to retrieve]"
            result["is_binary"] = True
        else:
            result["content"] = content
            result["is_binary"] = is_binary
            if is_binary:
                result["encoding"] = "base64"

        logger.info(f"Read file {storage_service}:{file_path} ({content_type})")

    return format_response(result)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def write_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    file_path: Annotated[str, "Full path for the file or folder (e.g., 'documents/new_report.txt' or 'new_folder/')"],
    content: Annotated[str, "File content (text or base64 encoded binary), empty for folders"] = "",
    is_base64: Annotated[bool, "Whether the content is base64 encoded"] = False,
    is_folder: Annotated[bool, "Create a folder instead of a file"] = False,
    create_path: Annotated[bool, "Create parent directories if they don't exist"] = True
) -> str:
    """Write content to a file or create a folder in a storage service.

    Creates new files, folders, or overwrites existing files.
    Supports text and binary content (via base64 encoding).

    Examples:
        Text file: write_file("local", "config/new_settings.json", '{"key": "value"}')
        Binary file: write_file("s3_bucket", "uploads/image.png", base64_content, is_base64=True)
        Create folder: write_file("local", "new_folder/", is_folder=True)
        Nested folder: write_file("local", "data/exports/2024/", is_folder=True, create_path=True)
        Create with path: write_file("local", "new/folder/file.txt", "content", create_path=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # For folders, ensure path ends with /
    if is_folder and not file_path.endswith("/"):
        file_path = file_path + "/"

    # Prepare the payload
    payload = {
        "path": file_path
    }

    if is_folder:
        payload["is_folder"] = True
    else:
        payload["content"] = content
        if is_base64:
            payload["content_type"] = "application/octet-stream"

    # Add parameter to create path if needed
    params = {}
    if create_path:
        params["check_exist"] = "false"

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{storage_service}/{file_path}",
        headers=headers,
        params=params,
        json_data=payload
    )

    item_type = "folder" if is_folder else "file"
    logger.info(f"Created {item_type} {storage_service}:{file_path}")

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "path": file_path,
        "type": item_type,
        "message": f"{item_type.capitalize()} '{file_path}' created successfully"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def delete_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    path: Annotated[str, "Path to file or folder to delete"],
    force: Annotated[bool, "Force deletion of non-empty folders"] = False
) -> str:
    """Delete a file or folder from a storage service.

    WARNING: This operation cannot be undone.

    Examples:
        Delete file: delete_file("local", "temp/old_file.txt")
        Delete folder: delete_file("s3_bucket", "old_data/", force=True)
        Delete from subfolder: delete_file("local", "backups/2023/january/")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if path.startswith("/"):
        path = path[1:]

    # Add force parameter for folders
    params = {}
    if force:
        params["force"] = "true"

    logger.warning(f"Deleting {storage_service}:{path}")

    response = make_dreamfactory_request(
        method="DELETE",
        url=f"{config['base_url']}/{storage_service}/{path}",
        headers=headers,
        params=params
    )

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "path": path,
        "message": f"Successfully deleted '{path}'"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def manage_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    source_path: Annotated[str, "Source file or folder path"],
    destination_path: Annotated[str, "Destination path"],
    operation: Annotated[str, "Operation to perform: 'copy' or 'move'"] = "copy",
    overwrite: Annotated[bool, "Overwrite if destination exists"] = False
) -> str:
    """Copy, move, or rename files and folders within a storage service.

    This unified tool handles both copy and move operations, including file renaming.

    Examples:
        Copy file: manage_file("local", "documents/report.pdf", "backups/report_backup.pdf")
        Move file: manage_file("local", "temp/file.txt", "permanent/file.txt", operation="move")
        Rename file: manage_file("local", "old_name.txt", "new_name.txt", operation="move")
        Copy folder: manage_file("local", "data/2023/", "archive/2023/")
        Move folder: manage_file("s3_bucket", "staging/", "production/", operation="move")
        Overwrite: manage_file("local", "current.json", "previous.json", overwrite=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Validate operation
    if operation not in ["copy", "move"]:
        raise RetryableToolError(
            f"Invalid operation: {operation}",
            additional_prompt_content="Operation must be 'copy' or 'move'"
        )

    # Clean up paths
    if source_path.startswith("/"):
        source_path = source_path[1:]
    if destination_path.startswith("/"):
        destination_path = destination_path[1:]

    # Build request
    payload = {
        "source": source_path,
        "destination": destination_path
    }

    params = {}
    if overwrite:
        params["overwrite"] = "true"

    # Determine endpoint based on operation
    endpoint = "_copy" if operation == "copy" else "_move"

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{storage_service}/{endpoint}",
        headers=headers,
        params=params,
        json_data=payload
    )

    action_verb = "Copied" if operation == "copy" else "Moved"
    logger.info(f"{action_verb} {source_path} to {destination_path} in {storage_service}")

    return format_response({
        "success": True,
        "operation": operation,
        "storage_service": storage_service,
        "source": source_path,
        "destination": destination_path,
        "message": f"Successfully {operation}d '{source_path}' to '{destination_path}'"
    })


