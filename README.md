# DreamFactory Arcade Toolkit

Streamlined toolkit for interacting with DreamFactory API Management Platform through Arcade AI.

## Overview

This toolkit provides 14 optimized tools for managing DreamFactory services, databases, and file storage. The toolkit has been carefully consolidated to minimize context overhead while maintaining full functionality.

## Installation

```bash
pip install arcade-dreamfactory
```

Or install from source:

```bash
git clone https://github.com/your-org/arcade-toolkit.git
cd arcade-toolkit
pip install -e .
```

## Configuration

### Required Secrets

Configure these secrets in your Arcade platform:

- `DREAM_FACTORY_BASE_URL` - Your DreamFactory instance URL (e.g., `https://demo.dreamfactory.com`)
- `DREAM_FACTORY_API_KEY` - Your DreamFactory API key with appropriate permissions

## Available Tools

### System Tools (2)

#### `list_services`
List all configured services in DreamFactory (databases, file storage, etc.)

```python
list_services()
list_services(service_type="mysql")  # Filter by type
```

#### `get_service_details`
Get detailed information about a specific service.

```python
get_service_details(service_id="mysql_prod")
```

### Database Tools (6)

#### `list_database_tables`
List all tables in a database service.

```python
list_database_tables("mysql_prod")
list_database_tables("postgres_db", include_schema=True)
```

#### `get_table_schema`
Get detailed schema information for a table.

```python
get_table_schema("mysql_prod", "users")
```

#### `query_database_table`
Query data with filtering, sorting, pagination, and ID-based retrieval.

```python
# Basic query
query_database_table("mysql_prod", "users", limit=10)

# With filter
query_database_table("mysql_prod", "users", filter="age > 25")

# By IDs
query_database_table("mysql_prod", "users", ids="1,2,3")

# Custom ID field
query_database_table("mysql_prod", "products", ids="ABC,DEF", id_field="sku")
```

#### `insert_records`
Insert one or more records into a table.

```python
insert_records("mysql_prod", "users", '[{"name": "John", "email": "john@example.com"}]')
```

#### `update_records`
Update records in a table.

```python
# Update by filter
update_records("mysql_prod", "users", '{"active": false}', filter="last_login < '2023-01-01'")

# Update by IDs
update_records("mysql_prod", "users", '{"status": "verified"}', ids="1,2,3")
```

#### `delete_records`
Delete records from a table.

```python
# Delete by filter
delete_records("mysql_prod", "logs", filter="created_at < '2023-01-01'")

# Delete by IDs
delete_records("mysql_prod", "users", ids="123,456")
```

### File Storage Tools (6)

#### `list_storage_services`
List all configured file storage services (local, S3, Azure, etc.)

```python
list_storage_services()
```

#### `list_files`
List and search files in a storage service.

```python
# List files
list_files("local", "/")

# Search files
list_files("local", "/", search_term="report", recursive=True)

# With pattern
list_files("local", "/logs", pattern="*.log")
```

#### `read_file`
Read file contents or metadata.

```python
# Read text file
read_file("local", "config/settings.json")

# Read binary file
read_file("s3_bucket", "images/logo.png", as_base64=True)

# Get metadata only
read_file("local", "large_file.zip", metadata_only=True)
```

#### `write_file`
Write files or create folders.

```python
# Write text file
write_file("local", "config/new.json", '{"key": "value"}')

# Write binary file
write_file("s3_bucket", "image.png", base64_content, is_base64=True)

# Create folder
write_file("local", "new_folder/", is_folder=True)
```

#### `delete_file`
Delete files or folders.

```python
# Delete file
delete_file("local", "temp/old_file.txt")

# Delete folder
delete_file("local", "old_data/", force=True)
```

#### `manage_file`
Copy or move files and folders.

```python
# Copy file
manage_file("local", "report.pdf", "backups/report.pdf")

# Move file
manage_file("local", "temp.txt", "permanent.txt", operation="move")

# Copy with overwrite
manage_file("local", "current.json", "previous.json", overwrite=True)
```

## Usage Example

```python
from arcade_dreamfactory.tools import (
    list_services,
    list_database_tables,
    query_database_table
)

# Discover available services
services = list_services()

# List tables in a database
tables = list_database_tables("mysql_production")

# Query data
users = query_database_table(
    "mysql_production",
    "users",
    filter="created_at >= '2024-01-01'",
    limit=100
)
```

## Architecture

The toolkit is organized into three modules:

- `system_tools.py` - Service discovery and management
- `database_tools.py` - Database operations and queries
- `file_tools.py` - File storage operations

All tools include:
- Comprehensive error handling
- Automatic retry logic for transient failures
- Type hints and validation
- Detailed logging

## Requirements

- Python 3.10+
- DreamFactory instance with API access
- Valid API key with appropriate permissions

## Support

For issues or questions, please contact your DreamFactory administrator or create an issue in the repository.

## License

[Your License]