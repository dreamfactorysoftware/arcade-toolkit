"""DreamFactory Arcade Toolkit - Streamlined API Management Tools.

This toolkit provides essential tools for interacting with DreamFactory API platform,
organized into three main categories:

1. System Tools: Service discovery and inspection
2. Database Tools: Table operations and data management
3. File Tools: Storage service file operations

All tools follow Arcade.dev best practices with comprehensive error handling
and clear tool descriptions to ensure proper tool selection.
"""

# System Management Tools
from .system_tools import (
    get_service_details,
    list_services,
)

# Database Operations Tools
from .database_tools import (
    delete_records,
    get_table_schema,
    insert_records,
    list_database_tables,
    query_database_table,
    update_records,
)

# File Storage Tools
from .file_tools import (
    delete_file,
    list_files,
    list_storage_services,
    manage_file,
    read_file,
    write_file,
)

__all__ = [
    # System Tools (2)
    "list_services",
    "get_service_details",
    # Database Tools (6)
    "list_database_tables",
    "get_table_schema",
    "query_database_table",
    "insert_records",
    "update_records",
    "delete_records",
    # File Tools (6)
    "list_storage_services",
    "list_files",
    "read_file",
    "write_file",
    "delete_file",
    "manage_file",
]