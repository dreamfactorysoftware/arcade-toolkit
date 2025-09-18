"""DreamFactory Database Operations Tools - Tables and Data Management."""

from typing import Annotated, Any, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.errors import RetryableToolError, ToolExecutionError
from loguru import logger

from .utils import (
    build_query_params,
    format_response,
    get_dreamfactory_config,
    make_dreamfactory_request,
)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def list_database_tables(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service to list tables from"],
    include_schema: Annotated[bool, "Include table schema information"] = False
) -> str:
    """List all tables in a database service.

    Use this to discover what tables are available in a database.
    This is typically the first step when exploring a database.

    Examples:
        Basic list: list_database_tables("mysql_prod")
        With schemas: list_database_tables("postgres_db", include_schema=True)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    params = {}
    if include_schema:
        params["include_schema"] = "true"

    try:
        response = make_dreamfactory_request(
            method="GET",
            url=f"{config['base_url']}/{service_name}/_table",
            headers=headers,
            params=params
        )

        tables = response.get("resource", [])
        logger.info(f"Found {len(tables)} tables in service {service_name}")

        # Extract just table names for cleaner response
        table_list = [t.get("name", t) for t in tables]

        return format_response({
            "service": service_name,
            "tables": table_list if not include_schema else tables,
            "count": len(tables)
        })

    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            raise ToolExecutionError(
                f"Service '{service_name}' not found. Use list_services() to see available services."
            ) from e
        raise


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def get_table_schema(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table to get schema for"]
) -> str:
    """Get detailed schema information for a database table.

    Returns column definitions, data types, constraints, and relationships.
    Use this to understand table structure before querying or modifying data.

    Examples:
        get_table_schema("mysql_prod", "users")
        get_table_schema("postgres_db", "orders")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{service_name}/_schema/{table_name}",
        headers=headers
    )

    # Extract key schema information
    schema_info = {
        "table": table_name,
        "service": service_name,
        "columns": []
    }

    if "field" in response:
        for field in response["field"]:
            column = {
                "name": field.get("name"),
                "type": field.get("type"),
                "db_type": field.get("db_type"),
                "required": field.get("required", False),
                "primary_key": field.get("is_primary_key", False),
                "auto_increment": field.get("auto_increment", False),
                "allows_null": field.get("allows_null", True),
                "default": field.get("default_value"),
                "length": field.get("length")
            }
            schema_info["columns"].append(column)

    # Include relationships if present
    if "related" in response:
        schema_info["relationships"] = response["related"]

    return format_response(schema_info)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def query_database_table(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table to query"],
    filter: Annotated[str, "SQL WHERE clause style filter (e.g., \"age > 25 AND city = 'NYC'\")"] = "",
    fields: Annotated[Optional[list], "List of fields to return (None for all fields)"] = None,
    limit: Annotated[Optional[int], "Maximum number of records to return (None for system default)"] = None,
    offset: Annotated[int, "Number of records to skip for pagination"] = 0,
    order: Annotated[str, "Field(s) to order by (e.g., 'created_at DESC, name ASC')"] = "",
    related: Annotated[Optional[list], "Related tables to include via joins"] = None,
    include_count: Annotated[bool, "Include total count of matching records"] = False
) -> str:
    """Query data from a database table with filtering, sorting, and pagination.

    This is the primary tool for retrieving data from databases.
    Supports complex filtering, field selection, and related data.

    Filter syntax supports:
        - Logical: AND, OR, NOT (with parentheses)
        - Comparison: =, !=, >, >=, <, <=
        - Pattern: LIKE, STARTS WITH, ENDS WITH, CONTAINS
        - Set: IN, NOT IN

    Examples:
        Simple query: query_database_table("mysql_prod", "users", limit=10)
        With filter: query_database_table("mysql_prod", "users", filter="age > 25 AND active = true")
        Specific fields: query_database_table("mysql_prod", "users", fields=["id", "name", "email"])
        With sorting: query_database_table("mysql_prod", "orders", order="created_at DESC", limit=100)
        With pagination: query_database_table("mysql_prod", "logs", limit=50, offset=100)
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    params = build_query_params(
        filter_str=filter,
        fields=fields or "*",
        limit=limit,
        offset=offset,
        order=order,
        related=related or "",
        include_count=include_count
    )

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{service_name}/_table/{table_name}",
        headers=headers,
        params=params
    )

    # Extract records and metadata
    records = response.get("resource", [])
    result = {
        "service": service_name,
        "table": table_name,
        "records": records,
        "count": len(records)
    }

    # Add total count if requested
    if include_count and "meta" in response and "count" in response["meta"]:
        result["total_count"] = response["meta"]["count"]
        result["has_more"] = response["meta"]["count"] > (offset + len(records))

    logger.info(f"Retrieved {len(records)} records from {service_name}.{table_name}")

    return format_response(result)


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def get_records_by_ids(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table"],
    ids: Annotated[list[Any], "List of record IDs to retrieve"],
    id_field: Annotated[str, "Name of the ID field (e.g., 'id', 'user_id')"] = "id",
    fields: Annotated[Optional[list], "List of fields to return"] = None
) -> str:
    """Get specific records from a table by their IDs.

    More efficient than using a filter when you know exact IDs.

    Examples:
        Single ID: get_records_by_ids("mysql_prod", "users", [123])
        Multiple IDs: get_records_by_ids("mysql_prod", "orders", [1, 2, 3, 4, 5])
        Custom ID field: get_records_by_ids("mysql_prod", "products", ["ABC123"], id_field="sku")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Build ID filter
    if len(ids) == 1:
        filter_str = f"{id_field} = {ids[0]}" if isinstance(ids[0], (int, float)) else f"{id_field} = '{ids[0]}'"
    else:
        id_list = ",".join(str(id) if isinstance(id, (int, float)) else f"'{id}'" for id in ids)
        filter_str = f"{id_field} IN ({id_list})"

    params = build_query_params(
        filter_str=filter_str,
        fields=fields or "*"
    )

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{service_name}/_table/{table_name}",
        headers=headers,
        params=params
    )

    records = response.get("resource", [])

    return format_response({
        "service": service_name,
        "table": table_name,
        "requested_ids": ids,
        "id_field": id_field,
        "records": records,
        "found": len(records),
        "not_found": len(ids) - len(records) if len(records) < len(ids) else 0
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def insert_records(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table to insert into"],
    records: Annotated[list[dict], "List of records to insert (each record is a dictionary)"],
    return_created: Annotated[bool, "Return the created records with auto-generated IDs"] = True
) -> str:
    """Insert one or more records into a database table.

    Records should be provided as a list of dictionaries, where each dictionary
    represents a row with column names as keys.

    Examples:
        Single record: insert_records("mysql_prod", "users", [{"name": "John", "email": "john@example.com"}])
        Multiple records: insert_records("mysql_prod", "logs", [{"event": "login"}, {"event": "logout"}])
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # DreamFactory expects records in a resource array
    payload = {"resource": records}

    # Add parameter to return created records
    params = {}
    if return_created:
        params["fields"] = "*"

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{service_name}/_table/{table_name}",
        headers=headers,
        params=params,
        json_data=payload
    )

    created_records = response.get("resource", [])

    return format_response({
        "success": True,
        "service": service_name,
        "table": table_name,
        "inserted_count": len(created_records) if created_records else len(records),
        "records": created_records if return_created else None,
        "message": f"Successfully inserted {len(records)} record(s) into {table_name}"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def update_records(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table to update"],
    updates: Annotated[dict, "Field-value pairs to update"],
    filter: Annotated[str, "SQL WHERE clause to identify records to update"] = "",
    ids: Annotated[list[Any] | None, "Specific IDs to update (alternative to filter)"] = None,
    id_field: Annotated[str, "Name of the ID field if using ids parameter"] = "id",
    return_updated: Annotated[bool, "Return the updated records"] = True
) -> str:
    """Update records in a database table.

    You must provide either a filter or specific IDs to identify which records to update.

    Examples:
        Update by filter: update_records("mysql_prod", "users", {"active": False}, filter="last_login < '2023-01-01'")
        Update by IDs: update_records("mysql_prod", "products", {"price": 99.99}, ids=[1, 2, 3])
        Update single field: update_records("mysql_prod", "orders", {"status": "shipped"}, filter="id = 123")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Build filter from IDs if provided
    if ids:
        if len(ids) == 1:
            filter = f"{id_field} = {ids[0]}" if isinstance(ids[0], (int, float)) else f"{id_field} = '{ids[0]}'"
        else:
            id_list = ",".join(str(id) if isinstance(id, (int, float)) else f"'{id}'" for id in ids)
            filter = f"{id_field} IN ({id_list})"
    elif not filter:
        raise RetryableToolError(
            "Must provide either 'filter' or 'ids' parameter",
            additional_prompt_content="Specify which records to update using a filter condition or list of IDs"
        )

    # Build request
    params = build_query_params(filter_str=filter)
    if return_updated:
        params["fields"] = "*"

    # DreamFactory expects updates in resource array format for batch updates
    payload = {"resource": [updates]}

    response = make_dreamfactory_request(
        method="PATCH",
        url=f"{config['base_url']}/{service_name}/_table/{table_name}",
        headers=headers,
        params=params,
        json_data=payload
    )

    updated_records = response.get("resource", [])

    return format_response({
        "success": True,
        "service": service_name,
        "table": table_name,
        "filter": filter,
        "updates": updates,
        "updated_count": len(updated_records) if updated_records else "unknown",
        "records": updated_records if return_updated else None,
        "message": f"Successfully updated records in {table_name}"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def delete_records(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    table_name: Annotated[str, "Name of the table to delete from"],
    filter: Annotated[str, "SQL WHERE clause to identify records to delete"] = "",
    ids: Annotated[list[Any] | None, "Specific IDs to delete (alternative to filter)"] = None,
    id_field: Annotated[str, "Name of the ID field if using ids parameter"] = "id"
) -> str:
    """Delete records from a database table.

    WARNING: This operation cannot be undone. Always verify your filter before deleting.

    You must provide either a filter or specific IDs to identify which records to delete.

    Examples:
        Delete by filter: delete_records("mysql_prod", "logs", filter="created_at < '2023-01-01'")
        Delete by IDs: delete_records("mysql_prod", "users", ids=[123, 456])
        Delete single record: delete_records("mysql_prod", "orders", filter="id = 789")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Build filter from IDs if provided
    if ids:
        if len(ids) == 1:
            filter = f"{id_field} = {ids[0]}" if isinstance(ids[0], (int, float)) else f"{id_field} = '{ids[0]}'"
        else:
            id_list = ",".join(str(id) if isinstance(id, (int, float)) else f"'{id}'" for id in ids)
            filter = f"{id_field} IN ({id_list})"
    elif not filter:
        raise RetryableToolError(
            "Must provide either 'filter' or 'ids' parameter",
            additional_prompt_content="Specify which records to delete using a filter condition or list of IDs"
        )

    params = build_query_params(filter_str=filter)

    logger.warning(f"Deleting records from {service_name}.{table_name} with filter: {filter}")

    response = make_dreamfactory_request(
        method="DELETE",
        url=f"{config['base_url']}/{service_name}/_table/{table_name}",
        headers=headers,
        params=params
    )

    # Extract deletion info
    deleted_info = response.get("resource", [])
    deleted_count = len(deleted_info) if deleted_info else "unknown"

    return format_response({
        "success": True,
        "service": service_name,
        "table": table_name,
        "filter": filter,
        "deleted_count": deleted_count,
        "message": f"Successfully deleted records from {table_name}"
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def execute_sql_query(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    sql: Annotated[str, "SQL query to execute"],
    params: Annotated[dict | None, "Parameter values for prepared statement"] = None
) -> str:
    """Execute a raw SQL query on the database (SELECT only for safety).

    Use this for complex queries that can't be expressed with the standard tools.
    Only SELECT statements are allowed through this interface for safety.

    Examples:
        Simple query: execute_sql_query("mysql_prod", "SELECT COUNT(*) FROM users")
        With joins: execute_sql_query("mysql_prod", "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id")
        With parameters: execute_sql_query("mysql_prod", "SELECT * FROM users WHERE age > :min_age", {"min_age": 25})
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Safety check - only allow SELECT queries
    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"):
        raise ToolExecutionError(
            "Only SELECT queries are allowed through this interface",
            additional_prompt_content="Use insert_records, update_records, or delete_records for data modifications"
        )

    # Build request payload
    payload = {"statement": sql}
    if params:
        payload["params"] = params

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{service_name}/_sql",
        headers=headers,
        json_data=payload
    )

    # Extract results
    if "resource" in response:
        results = response["resource"]
    elif "result" in response:
        results = response["result"]
    else:
        results = response

    return format_response({
        "service": service_name,
        "sql": sql,
        "params": params,
        "results": results,
        "row_count": len(results) if isinstance(results, list) else 1
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def get_stored_procedures(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"]
) -> str:
    """List all stored procedures available in a database service.

    Use this to discover what stored procedures can be called.

    Examples:
        get_stored_procedures("mysql_prod")
        get_stored_procedures("sqlserver_db")
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    response = make_dreamfactory_request(
        method="GET",
        url=f"{config['base_url']}/{service_name}/_proc",
        headers=headers
    )

    procedures = response.get("resource", [])

    return format_response({
        "service": service_name,
        "procedures": procedures,
        "count": len(procedures)
    })


@tool(requires_secrets=["DREAM_FACTORY_BASE_URL", "DREAM_FACTORY_API_KEY"])
def call_stored_procedure(
    context: ToolContext,
    service_name: Annotated[str, "Name of the database service"],
    procedure_name: Annotated[str, "Name of the stored procedure to call"],
    params: Annotated[dict | None, "Parameters to pass to the procedure"] = None
) -> str:
    """Call a stored procedure in the database.

    Examples:
        No parameters: call_stored_procedure("mysql_prod", "refresh_materialized_views")
        With parameters: call_stored_procedure("mysql_prod", "calculate_user_stats", {"user_id": 123})
    """
    config = get_dreamfactory_config(context)
    headers = {"X-DreamFactory-API-Key": config["api_key"]}

    # Build request
    payload = {}
    if params:
        payload["params"] = params

    response = make_dreamfactory_request(
        method="POST",
        url=f"{config['base_url']}/{service_name}/_proc/{procedure_name}",
        headers=headers,
        json_data=payload if params else None
    )

    return format_response({
        "service": service_name,
        "procedure": procedure_name,
        "params": params,
        "result": response
    })