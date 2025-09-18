"""DreamFactory Arcade Toolkit - Comprehensive API Management Tools.

This toolkit provides robust tools for interacting with DreamFactory API platform,
organized into three main categories:

1. System Tools: Service, role, and app management
2. Database Tools: Table operations and data management
3. File Tools: Storage service file operations

All tools follow Arcade.dev best practices with comprehensive error handling
and clear tool descriptions to ensure proper tool selection.
"""

# System Management Tools
from .system_tools import (
    create_app,
    create_database_api_complete,
    create_database_service,
    create_role,
    delete_service,
    get_service_details,
    list_apps,
    list_roles,
    list_services,
)

# Database Operations Tools
from .database_tools import (
    call_stored_procedure,
    delete_records,
    execute_sql_query,
    get_records_by_ids,
    get_stored_procedures,
    get_table_schema,
    insert_records,
    list_database_tables,
    query_database_table,
    update_records,
)

# File Storage Tools
from .file_tools import (
    copy_file,
    create_folder,
    delete_file,
    get_file_info,
    list_files,
    list_storage_services,
    move_file,
    read_file,
    search_files,
    write_file,
)

__all__ = [
    # System Tools
    "list_services",
    "get_service_details",
    "create_database_service",
    "delete_service",
    "list_roles",
    "create_role",
    "list_apps",
    "create_app",
    "create_database_api_complete",
    # Database Tools
    "list_database_tables",
    "get_table_schema",
    "query_database_table",
    "get_records_by_ids",
    "insert_records",
    "update_records",
    "delete_records",
    "execute_sql_query",
    "get_stored_procedures",
    "call_stored_procedure",
    # File Tools
    "list_storage_services",
    "list_files",
    "read_file",
    "write_file",
    "delete_file",
    "copy_file",
    "move_file",
    "create_folder",
    "search_files",
    "get_file_info",
]