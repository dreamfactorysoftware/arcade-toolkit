"""DreamFactory System Management Tools - Services, Roles, and Apps."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.errors import RetryableToolError
from loguru import logger

from .utils import (
    format_response,
    get_dreamfactory_config,
    make_dreamfactory_request,
    validate_database_type,
    validate_storage_type,
)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_services(
    context: ToolContext,
    service_type: Annotated[str, "Filter by service type (e.g., 'mysql', 's3', 'local')"] = "",
    include_schema: Annotated[bool, "Include service schema in response"] = False
) -> str:
    """List all configured services in DreamFactory.

    Use this to see what database and storage services are available.
    This is typically the first step in understanding what resources are accessible.

    Examples:
        List all services: list_services()
        List only MySQL services: list_services(service_type="mysql")
        List with schemas: list_services(include_schema=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    params = {}
    if service_type:
        # Validate and normalize the type
        if service_type in ["mysql", "pgsql", "sqlsrv", "sqlite", "mongodb"]:
            normalized = validate_database_type(service_type)
        else:
            normalized = validate_storage_type(service_type)
        params["filter"] = f"type={normalized}"
    if include_schema:
        params["include_schema"] = "true"

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/service",
        headers=headers,
        params=params
    )

    services = response.get("resource", [])
    logger.info(f"Found {len(services)} services")

    return format_response({
        "services": services,
        "count": len(services)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def get_service_details(
    context: ToolContext,
    service_id: Annotated[str, "Service ID or name to get details for"]
) -> str:
    """Get detailed information about a specific service.

    Use this to understand the configuration and capabilities of a service.

    Examples:
        By ID: get_service_details(service_id=5)
        By name: get_service_details(service_id="mysql_prod")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/service/{service_id}",
        headers=headers
    )

    return format_response(response)


