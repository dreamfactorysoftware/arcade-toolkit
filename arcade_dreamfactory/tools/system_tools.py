"""DreamFactory System Management Tools - Services, Roles, and Apps."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.errors import RetryableToolError, ToolExecutionError
from loguru import logger

from .utils import (
    VERB_FULL_ACCESS,
    VERB_GET,
    format_response,
    get_dreamfactory_config,
    make_dreamfactory_request,
    validate_database_type,
    validate_storage_type,
    wait_for_service_ready,
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


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def create_database_service(
    context: ToolContext,
    name: Annotated[str, "Unique name for the service (e.g., 'mysql_prod')"],
    database_type: Annotated[str, "Database type: mysql, pgsql, sqlsrv, sqlite, mongodb"],
    host: Annotated[str, "Database host (use 'localhost' for local databases)"],
    database: Annotated[str, "Database name to connect to"],
    username: Annotated[str, "Database username"],
    password: Annotated[str, "Database password"],
    port: Annotated[Optional[int], "Database port (defaults: MySQL=3306, PostgreSQL=5432, SQL Server=1433)"] = None,
    description: Annotated[str, "Service description"] = "",
    schema_name: Annotated[str, "Schema name (for PostgreSQL/SQL Server)"] = "",
    charset: Annotated[str, "Character set (default: utf8mb4 for MySQL)"] = "",
    options: Annotated[dict, "Additional driver-specific options"] = None
) -> str:
    """Create a new database service for API access.

    This creates the service configuration but does not create roles or API keys.
    Use create_role and create_app to set up access control after creating the service.

    Examples:
        MySQL: create_database_service("mysql_prod", "mysql", "localhost", "mydb", "user", "pass")
        PostgreSQL: create_database_service("pg_dev", "pgsql", "db.example.com", "appdb", "pguser", "pass", port=5432)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Validate and normalize database type
    db_type = validate_database_type(database_type)

    # Set default ports if not provided
    if port is None:
        default_ports = {
            "mysql": 3306,
            "pgsql": 5432,
            "sqlsrv": 1433,
            "sqlite": None,
            "mongodb": 27017,
            "oracle": 1521
        }
        port = default_ports.get(db_type)

    # Build service configuration
    service_config = {
        "name": name,
        "label": name,
        "description": description or f"{database_type} database service",
        "is_active": True,
        "type": db_type,
        "config": {
            "host": host,
            "database": database,
            "username": username,
            "password": password
        }
    }

    # Add port if applicable
    if port and db_type != "sqlite":
        service_config["config"]["port"] = port

    # Add schema for PostgreSQL/SQL Server
    if schema_name and db_type in ["pgsql", "sqlsrv"]:
        service_config["config"]["schema"] = schema_name

    # Add charset for MySQL
    if db_type == "mysql" and not charset:
        service_config["config"]["charset"] = "utf8mb4"
    elif charset:
        service_config["config"]["charset"] = charset

    # Add any additional options
    if options:
        service_config["config"]["options"] = options

    logger.info(f"Creating {db_type} service: {name}")

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/service",
        headers=headers,
        json_data=service_config
    )

    service_id = response.get("id")
    logger.info(f"Service created with ID: {service_id}")

    # Wait for service to be ready
    if wait_for_service_ready(config, name):
        return format_response({
            "success": True,
            "service_id": service_id,
            "service_name": name,
            "message": f"Database service '{name}' created successfully and is ready for use"
        })
    else:
        return format_response({
            "success": True,
            "service_id": service_id,
            "service_name": name,
            "warning": "Service created but may need additional time to become fully ready"
        })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def delete_service(
    context: ToolContext,
    service_id: Annotated[str, "Service ID or name to delete"]
) -> str:
    """Delete a service from DreamFactory.

    WARNING: This will permanently remove the service configuration.
    The underlying database/storage is not affected.

    Examples:
        By ID: delete_service(service_id=5)
        By name: delete_service(service_id="test_service")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    logger.warning(f"Deleting service: {service_id}")

    response = make_dreamfactory_request(
        method="DELETE",
        url=f"{config['base_url']}/system/service/{service_id}",
        headers=headers
    )

    return format_response({
        "success": True,
        "message": f"Service '{service_id}' deleted successfully"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_roles(
    context: ToolContext,
    include_services: Annotated[bool, "Include service access details"] = False
) -> str:
    """List all roles configured in DreamFactory.

    Roles define what services and resources users can access.

    Examples:
        Basic list: list_roles()
        With service details: list_roles(include_services=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    params = {}
    if include_services:
        params["related"] = "role_service_access_by_role_id"

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/role",
        headers=headers,
        params=params
    )

    roles = response.get("resource", [])
    logger.info(f"Found {len(roles)} roles")

    return format_response({
        "roles": roles,
        "count": len(roles)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def create_role(
    context: ToolContext,
    name: Annotated[str, "Unique name for the role"],
    service_name: Annotated[str, "Service name to grant access to"],
    access_level: Annotated[str, "Access level: 'read', 'write', or 'full'"],
    tables: Annotated[str, "Comma-separated list of tables to grant access to (empty for all tables)"] = "",
    description: Annotated[str, "Role description"] = ""
) -> str:
    """Create a role with specific permissions for a service.

    Roles define what operations users can perform on services.
    After creating a role, use create_app to generate an API key with this role.

    Access levels:
        - 'read': SELECT operations only
        - 'write': INSERT, UPDATE, DELETE operations
        - 'full': All operations including schema modifications

    Examples:
        Full access to all tables: create_role("admin_role", "mysql_prod", "full")
        Read-only to specific tables: create_role("reporting", "mysql_prod", "read", tables="users,orders")
        Write access to all tables: create_role("app_role", "postgres_db", "write")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Map access levels to verb masks
    access_mapping = {
        "read": VERB_GET,
        "write": VERB_FULL_ACCESS - VERB_GET,  # POST, PUT, PATCH, DELETE
        "full": VERB_FULL_ACCESS
    }

    if access_level not in access_mapping:
        raise RetryableToolError(
            f"Invalid access level: {access_level}",
            additional_prompt_content="Valid access levels are: 'read', 'write', or 'full'"
        )

    verb_mask = access_mapping[access_level]

    # Parse tables from comma-separated string
    table_list = [t.strip() for t in tables.split(',') if t.strip()] if tables else []

    # Build role configuration
    role_config = {
        "name": name,
        "description": description or f"{access_level} access to {service_name}",
        "is_active": True,
        "role_service_access_by_role_id": [
            {
                "service_id": service_name,
                "component": "_table/*" if not table_list else None,
                "verb_mask": verb_mask,
                "requestor_mask": 1,  # API access
                "filters": [],
                "filter_op": "AND"
            }
        ]
    }

    # If specific tables are provided, add individual permissions
    if table_list:
        role_config["role_service_access_by_role_id"] = []
        for table in table_list:
            role_config["role_service_access_by_role_id"].append({
                "service_id": service_name,
                "component": f"_table/{table}/*",
                "verb_mask": verb_mask,
                "requestor_mask": 1,
                "filters": [],
                "filter_op": "AND"
            })

        # Also add schema access for the specified tables
        role_config["role_service_access_by_role_id"].append({
            "service_id": service_name,
            "component": "_schema/*",
            "verb_mask": VERB_GET,  # Read-only schema access
            "requestor_mask": 1,
            "filters": [],
            "filter_op": "AND"
        })

    logger.info(f"Creating role '{name}' with {access_level} access to {service_name}")

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/role",
        headers=headers,
        json_data=role_config
    )

    role_id = response.get("id")
    return format_response({
        "success": True,
        "role_id": role_id,
        "role_name": name,
        "service": service_name,
        "access_level": access_level,
        "tables": table_list if table_list else "all",
        "message": f"Role '{name}' created successfully with {access_level} access"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_apps(
    context: ToolContext,
    include_role: Annotated[bool, "Include role details"] = False
) -> str:
    """List all applications (API keys) configured in DreamFactory.

    Apps represent API keys that can be used to access services.

    Examples:
        Basic list: list_apps()
        With role details: list_apps(include_role=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    params = {}
    if include_role:
        params["related"] = "role_by_role_id"

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/app",
        headers=headers,
        params=params
    )

    apps = response.get("resource", [])
    logger.info(f"Found {len(apps)} apps")

    return format_response({
        "apps": apps,
        "count": len(apps)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def create_app(
    context: ToolContext,
    name: Annotated[str, "Unique name for the app"],
    role_name: Annotated[str, "Role name to assign to this app"],
    description: Annotated[str, "App description"] = ""
) -> str:
    """Create an application with an API key for accessing services.

    This generates an API key that can be used to access services based on the assigned role's permissions.
    The API key should be stored securely and used in the X-DreamFactory-Api-Key header.

    Examples:
        create_app("mobile_app", "mobile_role")
        create_app("reporting_tool", "read_only_role", description="Power BI connector")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # First, get the role ID
    role_response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/system/role",
        headers=headers,
        params={"filter": f"name='{role_name}'"}
    )

    roles = role_response.get("resource", [])
    if not roles:
        raise ToolExecutionError(f"Role '{role_name}' not found. Please create the role first.")

    role_id = roles[0]["id"]

    # Create the app
    app_config = {
        "name": name,
        "description": description or f"API key for {name}",
        "is_active": True,
        "type": 0,  # API Key type
        "role_id": role_id
    }

    logger.info(f"Creating app '{name}' with role '{role_name}'")

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/app",
        headers=headers,
        json_data=app_config
    )

    app_id = response.get("id")
    api_key = response.get("api_key")

    return format_response({
        "success": True,
        "app_id": app_id,
        "app_name": name,
        "api_key": api_key,
        "role": role_name,
        "message": f"App '{name}' created successfully",
        "usage": f"Use this API key in the 'X-DreamFactory-Api-Key' header for API requests"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def create_database_api_complete(
    context: ToolContext,
    service_name: Annotated[str, "Unique name for the service (e.g., 'mysql_prod')"],
    database_type: Annotated[str, "Database type: mysql, pgsql, sqlsrv, sqlite, mongodb"],
    host: Annotated[str, "Database host"],
    database: Annotated[str, "Database name"],
    username: Annotated[str, "Database username"],
    password: Annotated[str, "Database password"],
    port: Annotated[Optional[int], "Database port (uses defaults if not specified)"] = None,
    role_name: Annotated[str, "Name for the role to create"] = "",
    app_name: Annotated[str, "Name for the app to create"] = "",
    access_level: Annotated[str, "Access level: 'read', 'write', or 'full'"] = "full"
) -> str:
    """Complete one-step setup: Create database service, role, and API key.

    This is the recommended way to set up database API access.
    It combines create_database_service, create_role, and create_app into one operation.

    Examples:
        MySQL with full access:
            create_database_api_complete("mysql_prod", "mysql", "localhost", "mydb", "user", "pass")

        PostgreSQL with read-only access:
            create_database_api_complete("pg_analytics", "pgsql", "db.example.com", "analytics",
                                        "reader", "pass", port=5432, access_level="read")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Generate default names if not provided
    if not role_name:
        role_name = f"{service_name}_role"
    if not app_name:
        app_name = f"{service_name}_app"

    # Step 1: Create the database service
    db_type = validate_database_type(database_type)

    # Set default ports
    if port is None:
        default_ports = {
            "mysql": 3306,
            "pgsql": 5432,
            "sqlsrv": 1433,
            "mongodb": 27017
        }
        port = default_ports.get(db_type)

    service_config = {
        "name": service_name,
        "label": service_name,
        "description": f"{database_type} database service",
        "is_active": True,
        "type": db_type,
        "config": {
            "host": host,
            "database": database,
            "username": username,
            "password": password
        }
    }

    if port and db_type != "sqlite":
        service_config["config"]["port"] = port

    logger.info(f"Creating complete API setup for {service_name}")

    # Create service
    service_response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/service",
        headers=headers,
        json_data=service_config
    )

    service_id = service_response.get("id")

    # Wait for service to be ready
    service_ready = wait_for_service_ready(config, service_name)

    # Step 2: Create role with permissions
    access_mapping = {
        "read": VERB_GET,
        "write": VERB_FULL_ACCESS - VERB_GET,
        "full": VERB_FULL_ACCESS
    }
    verb_mask = access_mapping.get(access_level, VERB_FULL_ACCESS)

    role_config = {
        "name": role_name,
        "description": f"{access_level} access to {service_name}",
        "is_active": True,
        "role_service_access_by_role_id": [
            {
                "service_id": service_id,
                "component": "_table/*",
                "verb_mask": verb_mask,
                "requestor_mask": 1,
                "filters": [],
                "filter_op": "AND"
            },
            {
                "service_id": service_id,
                "component": "_schema/*",
                "verb_mask": VERB_GET,
                "requestor_mask": 1,
                "filters": [],
                "filter_op": "AND"
            }
        ]
    }

    role_response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/role",
        headers=headers,
        json_data=role_config
    )

    role_id = role_response.get("id")

    # Step 3: Create app with API key
    app_config = {
        "name": app_name,
        "description": f"API key for {service_name}",
        "is_active": True,
        "type": 0,
        "role_id": role_id
    }

    app_response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/system/app",
        headers=headers,
        json_data=app_config
    )

    api_key = app_response.get("api_key")

    # Get base URL without /api/v2
    base_url = config["base_url"].replace("/api/v2", "")

    return format_response({
        "success": True,
        "service": {
            "id": service_id,
            "name": service_name,
            "type": db_type,
            "status": "ready" if service_ready else "initializing"
        },
        "role": {
            "id": role_id,
            "name": role_name,
            "access_level": access_level
        },
        "app": {
            "name": app_name,
            "api_key": api_key
        },
        "api_endpoint": f"{base_url}/api/v2/{service_name}",
        "usage": {
            "headers": {"X-DreamFactory-Api-Key": api_key},
            "example_endpoints": [
                f"GET {base_url}/api/v2/{service_name}/_table",
                f"GET {base_url}/api/v2/{service_name}/_table/{{table_name}}"
            ]
        },
        "message": f"Database API successfully created for {service_name}"
    })