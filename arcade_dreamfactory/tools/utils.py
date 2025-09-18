"""Utility functions for DreamFactory API interactions."""

import json
import time
from typing import Any, Optional, TypedDict, Union

import httpx
from arcade_tdk import ToolContext
from arcade_tdk.errors import (
    ContextRequiredToolError,
    FatalToolError,
    RetryableToolError,
    ToolExecutionError,
    UpstreamError,
)
from loguru import logger

# Constants
RETRY_AFTER_MS = 500
MAX_RETRIES = 3
SERVICE_READY_POLL_INTERVAL = 2  # seconds
SERVICE_READY_MAX_ATTEMPTS = 10

# Verb masks for DreamFactory permissions
VERB_GET = 1
VERB_POST = 2
VERB_PUT = 4
VERB_PATCH = 8
VERB_DELETE = 16
VERB_FULL_ACCESS = 31


class DreamFactoryConfig(TypedDict):
    """Configuration for DreamFactory API connection."""

    base_url: str
    api_key: str


def get_dreamfactory_config(context: ToolContext) -> DreamFactoryConfig:
    """Get DreamFactory configuration from context secrets.

    Args:
        context: The tool context containing secrets

    Returns:
        DreamFactoryConfig dictionary with base_url and api_key

    Raises:
        ContextRequiredToolError: If required secrets are not configured
    """
    try:
        base_url = context.get_secret("DREAM_FACTORY_BASE_URL")
        api_key = context.get_secret("DREAM_FACTORY_API_KEY")

        if not base_url or not api_key:
            raise ContextRequiredToolError(
                "DreamFactory configuration missing",
                additional_prompt_content="Please ensure DREAM_FACTORY_BASE_URL and DREAM_FACTORY_API_KEY are configured in Arcade secrets"
            )

        # Ensure base_url ends with /api/v2
        if not base_url.endswith("/api/v2"):
            if base_url.endswith("/"):
                base_url = base_url + "api/v2"
            else:
                base_url = base_url + "/api/v2"

        return {"base_url": base_url, "api_key": api_key}
    except Exception as e:
        raise ContextRequiredToolError(
            f"Failed to get DreamFactory configuration: {e}",
            additional_prompt_content="Please check that your Arcade secrets are properly configured"
        ) from e


def make_dreamfactory_request(
    method: str,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    json_data: dict[str, Any] | None = None,
    retry_on_error: bool = True
) -> dict[str, Any]:
    """Make a request to DreamFactory API with error handling.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Full URL for the request
        headers: Request headers including API key
        params: Query parameters
        json_data: JSON payload for POST/PUT requests
        retry_on_error: Whether to raise RetryableToolError on failure

    Returns:
        JSON response from the API

    Raises:
        RetryableToolError: For temporary failures that can be retried
        FatalToolError: For permanent failures
        UpstreamError: For service-specific errors
    """
    try:
        logger.debug(f"Making {method} request to {url}")

        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30.0
        )

        # Check for successful response
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                # Some endpoints return empty responses
                return {"success": True}

        # Handle error responses
        error_msg = f"DreamFactory API error (HTTP {response.status_code})"
        try:
            error_data = response.json()
            if "error" in error_data:
                error_detail = error_data["error"]
                if isinstance(error_detail, dict) and "message" in error_detail:
                    error_msg = error_detail["message"]
                else:
                    error_msg = str(error_detail)
        except json.JSONDecodeError:
            error_msg = f"{error_msg}: {response.text}"

        # Determine error type based on status code
        if response.status_code == 401:
            raise ContextRequiredToolError(
                "Authentication failed",
                additional_prompt_content="Please check your API key is valid and has the required permissions"
            )
        elif response.status_code == 403:
            raise FatalToolError(f"Permission denied: {error_msg}")
        elif response.status_code == 404:
            raise ToolExecutionError(f"Resource not found: {error_msg}")
        elif response.status_code >= 500:
            if retry_on_error:
                raise RetryableToolError(
                    f"Server error: {error_msg}",
                    retry_after_ms=RETRY_AFTER_MS
                )
            else:
                raise UpstreamError(f"DreamFactory server error: {error_msg}")
        else:
            raise ToolExecutionError(f"Request failed: {error_msg}")

    except httpx.TimeoutException as e:
        if retry_on_error:
            raise RetryableToolError(
                "Request timed out - DreamFactory may be under load",
                retry_after_ms=RETRY_AFTER_MS * 2
            ) from e
        else:
            raise UpstreamError("DreamFactory connection timeout") from e
    except httpx.ConnectError as e:
        raise ContextRequiredToolError(
            "Cannot connect to DreamFactory",
            additional_prompt_content="Please verify the DREAM_FACTORY_BASE_URL is correct and the server is running"
        ) from e
    except (httpx.RequestError, Exception) as e:
        if retry_on_error:
            raise RetryableToolError(
                f"Request failed: {str(e)}",
                retry_after_ms=RETRY_AFTER_MS
            ) from e
        else:
            raise UpstreamError(f"DreamFactory request error: {str(e)}") from e


def build_query_params(
    filter_str: str = "",
    fields: Union[str, list] = "*",
    limit: Optional[int] = None,
    offset: int = 0,
    order: str = "",
    related: Union[str, list] = "",
    group: str = "",
    having: str = "",
    include_count: bool = False,
    include_schema: bool = False
) -> dict[str, str | int]:
    """Build query parameters for DreamFactory API requests.

    Args:
        filter_str: SQL WHERE clause style filter
        fields: Fields to return (* for all)
        limit: Maximum number of records
        offset: Number of records to skip
        order: Field(s) to order by
        related: Related tables to include
        group: GROUP BY clause
        having: HAVING clause
        include_count: Include total count in response
        include_schema: Include schema in response

    Returns:
        Dictionary of query parameters
    """
    params: dict[str, str | int] = {}

    if filter_str:
        params["filter"] = filter_str
    if fields and fields != "*":
        params["fields"] = fields if isinstance(fields, str) else ",".join(fields)
    if limit is not None:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if order:
        params["order"] = order
    if related:
        params["related"] = related if isinstance(related, str) else ",".join(related)
    if group:
        params["group"] = group
    if having:
        params["having"] = having
    if include_count:
        params["include_count"] = "true"
    if include_schema:
        params["include_schema"] = "true"

    return params


def wait_for_service_ready(
    config: DreamFactoryConfig,
    service_name: str,
    max_attempts: int = SERVICE_READY_MAX_ATTEMPTS
) -> bool:
    """Poll a service until it's ready to handle requests.

    Args:
        config: DreamFactory configuration
        service_name: Name of the service to check
        max_attempts: Maximum number of polling attempts

    Returns:
        True if service is ready, False if timeout
    """
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    for attempt in range(max_attempts):
        try:
            # Try to access the service's schema endpoint
            response = httpx.get(
                f"{config['base_url']}/{service_name}/_schema",
                headers=headers,
                timeout=5.0
            )

            if response.status_code == 200:
                logger.info(f"Service {service_name} is ready after {attempt + 1} attempts")
                return True
            elif response.status_code == 404:
                # Service doesn't exist yet
                pass
            else:
                # Some other error, but service exists
                logger.warning(f"Service {service_name} returned status {response.status_code}")

        except (httpx.TimeoutException, httpx.ConnectError):
            # Expected during service initialization
            pass
        except Exception as e:
            logger.warning(f"Error checking service readiness: {e}")

        if attempt < max_attempts - 1:
            time.sleep(SERVICE_READY_POLL_INTERVAL)

    logger.error(f"Service {service_name} did not become ready after {max_attempts} attempts")
    return False


def format_response(data: Any, pretty: bool = False) -> str:
    """Format response data as JSON string.

    Args:
        data: Data to format
        pretty: Whether to use pretty printing

    Returns:
        JSON string representation
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)


def validate_database_type(db_type: str) -> str:
    """Validate and normalize database type.

    Args:
        db_type: Database type string

    Returns:
        Normalized database type

    Raises:
        RetryableToolError: If database type is invalid
    """
    valid_types = {
        "mysql": "mysql",
        "mariadb": "mysql",
        "postgres": "pgsql",
        "postgresql": "pgsql",
        "pgsql": "pgsql",
        "mssql": "sqlsrv",
        "sqlserver": "sqlsrv",
        "sqlsrv": "sqlsrv",
        "sqlite": "sqlite",
        "sqlite3": "sqlite",
        "mongodb": "mongodb",
        "mongo": "mongodb",
        "cosmosdb": "cosmosdb",
        "cosmos": "cosmosdb",
        "oracle": "oracle",
        "firebird": "firebird",
    }

    normalized = db_type.lower().replace(" ", "").replace("-", "").replace("_", "")

    if normalized not in valid_types:
        raise RetryableToolError(
            f"Invalid database type: {db_type}",
            additional_prompt_content=f"Valid database types are: {', '.join(set(valid_types.values()))}"
        )

    return valid_types[normalized]


def validate_storage_type(storage_type: str) -> str:
    """Validate and normalize storage service type.

    Args:
        storage_type: Storage type string

    Returns:
        Normalized storage type

    Raises:
        RetryableToolError: If storage type is invalid
    """
    valid_types = {
        "local": "local",
        "localfile": "local",
        "s3": "s3",
        "aws": "s3",
        "amazons3": "s3",
        "azure": "azure",
        "azureblob": "azure",
        "blobstorage": "azure",
        "ftp": "ftp",
        "sftp": "sftp",
        "ssh": "sftp",
        "webdav": "webdav",
        "dav": "webdav",
    }

    normalized = storage_type.lower().replace(" ", "").replace("-", "").replace("_", "")

    if normalized not in valid_types:
        raise RetryableToolError(
            f"Invalid storage type: {storage_type}",
            additional_prompt_content=f"Valid storage types are: {', '.join(set(valid_types.values()))}"
        )

    return valid_types[normalized]