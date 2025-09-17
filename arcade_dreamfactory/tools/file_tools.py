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
    pattern: Annotated[str, "File pattern to match (e.g., '*.txt', '*.pdf')"] = ""
) -> str:
    """List files and folders in a storage service.

    Use this to explore the contents of file storage services.
    Supports local storage, S3, Azure Blob, FTP, SFTP, and WebDAV.

    Examples:
        List root: list_files("local", "/")
        List subfolder: list_files("s3_bucket", "documents/")
        List recursively: list_files("local", "/data", recursive=True)
        Filter by pattern: list_files("local", "/logs", pattern="*.log")
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

    for item in items:
        item_info = {
            "name": item.get("name"),
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

    if include_folders:
        result["folders"] = folders
        result["folder_count"] = len(folders)

    logger.info(f"Listed {len(files)} files and {len(folders)} folders in {storage_service}:{path}")

    return format_response(result)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def read_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    file_path: Annotated[str, "Full path to the file (e.g., 'documents/report.txt')"],
    as_base64: Annotated[bool, "Return binary files as base64 encoded string"] = False
) -> str:
    """Read the contents of a file from a storage service.

    Returns text content directly or binary content as base64 if requested.
    Automatically detects binary files and encodes them.

    Examples:
        Text file: read_file("local", "config/settings.json")
        Binary file: read_file("s3_bucket", "images/logo.png", as_base64=True)
        From subfolder: read_file("local", "data/exports/report.csv")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # Add parameter to get content
    params = {"include_content": "true"}

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{storage_service}/{file_path}",
        headers=headers,
        params=params
    )

    # Extract content
    content = response.get("content", "")
    content_type = response.get("content_type", "text/plain")

    # Check if content is already base64 encoded (DreamFactory does this for binary files)
    is_binary = "image" in content_type or "application" in content_type or is_binary_content(str(content))

    result = {
        "storage_service": storage_service,
        "file_path": file_path,
        "content_type": content_type,
        "size": response.get("content_length", 0),
        "modified": response.get("last_modified")
    }

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
    file_path: Annotated[str, "Full path for the file (e.g., 'documents/new_report.txt')"],
    content: Annotated[str, "File content (text or base64 encoded binary)"],
    is_base64: Annotated[bool, "Whether the content is base64 encoded"] = False,
    create_path: Annotated[bool, "Create parent directories if they don't exist"] = True
) -> str:
    """Write content to a file in a storage service.

    Creates a new file or overwrites an existing one.
    Supports text and binary content (via base64 encoding).

    Examples:
        Text file: write_file("local", "config/new_settings.json", '{"key": "value"}')
        Binary file: write_file("s3_bucket", "uploads/image.png", base64_content, is_base64=True)
        Create with path: write_file("local", "new/folder/file.txt", "content", create_path=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # Prepare the payload
    payload = {
        "path": file_path,
        "content": content
    }

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

    logger.info(f"Wrote file {storage_service}:{file_path}")

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "file_path": file_path,
        "message": f"File '{file_path}' written successfully"
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
def copy_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    source_path: Annotated[str, "Source file or folder path"],
    destination_path: Annotated[str, "Destination path"],
    overwrite: Annotated[bool, "Overwrite if destination exists"] = False
) -> str:
    """Copy a file or folder within a storage service.

    Examples:
        Copy file: copy_file("local", "documents/report.pdf", "backups/report_backup.pdf")
        Copy folder: copy_file("local", "data/2023/", "archive/2023/")
        Overwrite existing: copy_file("s3_bucket", "current.json", "previous.json", overwrite=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

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

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{storage_service}/_copy",
        headers=headers,
        params=params,
        json_data=payload
    )

    logger.info(f"Copied {source_path} to {destination_path} in {storage_service}")

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "source": source_path,
        "destination": destination_path,
        "message": f"Successfully copied '{source_path}' to '{destination_path}'"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def move_file(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    source_path: Annotated[str, "Source file or folder path"],
    destination_path: Annotated[str, "Destination path"],
    overwrite: Annotated[bool, "Overwrite if destination exists"] = False
) -> str:
    """Move or rename a file or folder within a storage service.

    Examples:
        Rename file: move_file("local", "old_name.txt", "new_name.txt")
        Move file: move_file("local", "temp/file.txt", "permanent/file.txt")
        Move folder: move_file("s3_bucket", "staging/", "production/")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

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

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{storage_service}/_move",
        headers=headers,
        params=params,
        json_data=payload
    )

    logger.info(f"Moved {source_path} to {destination_path} in {storage_service}")

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "source": source_path,
        "destination": destination_path,
        "message": f"Successfully moved '{source_path}' to '{destination_path}'"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def create_folder(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    folder_path: Annotated[str, "Path for the new folder (e.g., 'documents/reports/2024/')"],
    create_parents: Annotated[bool, "Create parent folders if they don't exist"] = True
) -> str:
    """Create a new folder in a storage service.

    Examples:
        Simple folder: create_folder("local", "new_folder/")
        Nested folder: create_folder("local", "data/exports/2024/", create_parents=True)
        In S3: create_folder("s3_bucket", "uploads/images/")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Ensure path ends with / for folder
    if not folder_path.endswith("/"):
        folder_path = folder_path + "/"

    # Clean up path
    if folder_path.startswith("/"):
        folder_path = folder_path[1:]

    # Create folder
    payload = {
        "path": folder_path,
        "is_folder": True
    }

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{storage_service}/{folder_path}",
        headers=headers,
        json_data=payload
    )

    logger.info(f"Created folder {storage_service}:{folder_path}")

    return format_response({
        "success": True,
        "storage_service": storage_service,
        "folder_path": folder_path,
        "message": f"Folder '{folder_path}' created successfully"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def search_files(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    search_term: Annotated[str, "Term to search for in file names"],
    path: Annotated[str, "Starting path for search (use '/' for root)"] = "/",
    recursive: Annotated[bool, "Search in subdirectories"] = True,
    case_sensitive: Annotated[bool, "Case-sensitive search"] = False
) -> str:
    """Search for files by name pattern in a storage service.

    Searches file names for the specified term.

    Examples:
        Search all: search_files("local", "report")
        Search in folder: search_files("local", "backup", path="archives/")
        Case sensitive: search_files("s3_bucket", "Config", case_sensitive=True)
        Pattern search: search_files("local", "*.log")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if path != "/" and path.startswith("/"):
        path = path[1:]

    # Use pattern matching in list operation
    params = {
        "recursive": "true" if recursive else "false",
        "pattern": f"*{search_term}*" if "*" not in search_term else search_term
    }

    url = f"{config['base_url']}/{storage_service}"
    if path and path != "/":
        url = f"{url}/{path}"

    response = make_dreamfactory_request(
        method="GET",
        url=url,
        headers=headers,
        params=params
    )

    # Filter results based on case sensitivity
    items = response.get("resource", [])
    matched_files = []

    search_lower = search_term.lower() if not case_sensitive else search_term

    for item in items:
        if item.get("type") != "folder":
            name = item.get("name", "")
            name_to_check = name if case_sensitive else name.lower()

            # Check if search term is in the name
            if "*" in search_term:
                # Pattern matching was already done by the API
                matched_files.append({
                    "name": name,
                    "path": item.get("path"),
                    "size": item.get("content_length", 0),
                    "modified": item.get("last_modified"),
                    "type": item.get("content_type", "")
                })
            elif search_lower in name_to_check:
                matched_files.append({
                    "name": name,
                    "path": item.get("path"),
                    "size": item.get("content_length", 0),
                    "modified": item.get("last_modified"),
                    "type": item.get("content_type", "")
                })

    logger.info(f"Found {len(matched_files)} files matching '{search_term}' in {storage_service}:{path}")

    return format_response({
        "storage_service": storage_service,
        "search_term": search_term,
        "search_path": path,
        "recursive": recursive,
        "matched_files": matched_files,
        "count": len(matched_files)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def get_file_info(
    context: ToolContext,
    storage_service: Annotated[str, "Name of the storage service"],
    file_path: Annotated[str, "Full path to the file"]
) -> str:
    """Get metadata information about a file without reading its content.

    Returns file size, modification date, content type, and other metadata.

    Examples:
        get_file_info("local", "documents/report.pdf")
        get_file_info("s3_bucket", "images/logo.png")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Clean up path
    if file_path.startswith("/"):
        file_path = file_path[1:]

    # Get file info without content
    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{storage_service}/{file_path}",
        headers=headers,
        params={"include_content": "false"}
    )

    return format_response({
        "storage_service": storage_service,
        "file_path": file_path,
        "name": response.get("name"),
        "size": response.get("content_length", 0),
        "content_type": response.get("content_type"),
        "modified": response.get("last_modified"),
        "created": response.get("created_date"),
        "is_folder": response.get("type") == "folder",
        "metadata": response.get("metadata", {})
    })