<div style="display: flex; justify-content: center; align-items: center;">
  <img
    src="https://docs.arcade.dev/images/logo/arcade-logo.png"
    style="width: 250px;"
  >
</div>

<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
  <img src="https://img.shields.io/github/v/release/thekevinm/dreamfactory" alt="GitHub release" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python version" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" style="margin: 0 2px;">
  <img src="https://img.shields.io/pypi/v/arcade_dreamfactory" alt="PyPI version" style="margin: 0 2px;">
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <a href="https://github.com/thekevinm/dreamfactory" target="_blank">
    <img src="https://img.shields.io/github/stars/thekevinm/dreamfactory" alt="GitHub stars" style="margin: 0 2px;">
  </a>
  <a href="https://github.com/thekevinm/dreamfactory/fork" target="_blank">
    <img src="https://img.shields.io/github/forks/thekevinm/dreamfactory" alt="GitHub forks" style="margin: 0 2px;">
  </a>
</div>

<br>
<br>

# Arcade DreamFactory Toolkit

A robust and comprehensive toolkit for interacting with DreamFactory API platform through Arcade AI. This toolkit provides enterprise-grade tools for database operations, file storage management, and system administration with advanced error handling and clear tool descriptions for optimal AI agent selection.

## Features

### 🗄️ **Database Operations**
- List tables and explore schemas
- Query data with advanced filtering, sorting, and pagination
- Insert, update, and delete records
- Execute SQL queries and stored procedures
- Optimized for MySQL, PostgreSQL, SQL Server, SQLite, and MongoDB

### 📁 **File Storage Management**
- Support for multiple storage backends (Local, S3, Azure Blob, FTP, SFTP, WebDAV)
- File and folder operations (read, write, copy, move, delete)
- Search files across storage services
- Binary file handling with base64 encoding

### ⚙️ **System Administration**
- Create and manage database services
- Role-based access control
- API key generation and management
- One-step database API setup
- Service health monitoring

## Installation

### Prerequisites
- Python 3.10+
- Poetry package manager
- DreamFactory instance (local or cloud)
- Arcade AI account

### Setup Steps

1. **Clone and Install**
```bash
git clone https://github.com/yourusername/arcade-toolkit.git
cd arcade-toolkit
make install
```

2. **Configure Arcade Secrets**

Add your DreamFactory credentials to Arcade Secrets:
- `DREAM_FACTORY_BASE_URL`: Your DreamFactory instance URL (e.g., `https://your-instance.dreamfactory.com`)
- `DREAM_FACTORY_API_KEY`: Your system-level API key

![Screenshot 2025-06-11 at 4 06 26 PM](https://github.com/user-attachments/assets/1807a014-ea46-450d-9509-484208ff3b7c)
![Screenshot 2025-06-11 at 4 06 51 PM](https://github.com/user-attachments/assets/19ef7619-f7c7-43f3-b609-e9bcc42b38bd)

3. **Build and Deploy**
```bash
# Build the toolkit
make build

# Deploy to Arcade Cloud
arcade deploy

# Or serve locally for development
arcade serve
```

## Usage Examples

### Quick Start: Complete Database API Setup

```python
# One-step setup: Creates service, role, and API key
create_database_api_complete(
    service_name="production_db",
    database_type="mysql",
    host="db.example.com",
    database="myapp",
    username="dbuser",
    password="secure_password",
    access_level="full"
)
# Returns: API endpoint, API key, and usage instructions
```

### Database Operations

```python
# List all tables in a database
list_database_tables("production_db")

# Query data with filtering and pagination
query_database_table(
    service_name="production_db",
    table_name="users",
    filter="age > 25 AND status = 'active'",
    fields=["id", "name", "email"],
    order="created_at DESC",
    limit=50,
    offset=0
)

# Insert records
insert_records(
    service_name="production_db",
    table_name="events",
    records=[
        {"event_type": "login", "user_id": 123, "timestamp": "2024-01-15T10:30:00"},
        {"event_type": "purchase", "user_id": 456, "amount": 99.99}
    ]
)

# Update records by filter
update_records(
    service_name="production_db",
    table_name="users",
    updates={"last_login": "2024-01-15T10:30:00"},
    filter="id = 123"
)
```

### File Storage Operations

```python
# List files in a storage service
list_files(
    storage_service="s3_bucket",
    path="documents/",
    recursive=True,
    pattern="*.pdf"
)

# Read a file
read_file(
    storage_service="local",
    file_path="config/settings.json"
)

# Write a file
write_file(
    storage_service="s3_bucket",
    file_path="reports/monthly_report.txt",
    content="Report content here...",
    create_path=True
)

# Search for files
search_files(
    storage_service="local",
    search_term="invoice",
    path="documents/",
    recursive=True
)
```

### System Management

```python
# Create a database service
create_database_service(
    name="analytics_db",
    database_type="postgresql",
    host="postgres.example.com",
    database="analytics",
    username="analyst",
    password="secure_pass",
    port=5432
)

# Create a role with specific permissions
create_role(
    name="reporting_role",
    service_name="analytics_db",
    access_level="read",
    tables=["sales", "customers", "products"]
)

# Generate an API key
create_app(
    name="bi_dashboard",
    role_name="reporting_role",
    description="Power BI connector"
)
```

## Tool Organization

The toolkit is organized into three main modules for clear separation of concerns:

### System Tools (`system_tools.py`)
- `list_services` - View all configured services
- `create_database_service` - Set up new database connections
- `create_role` - Define access permissions
- `create_app` - Generate API keys
- `create_database_api_complete` - One-step API setup

### Database Tools (`database_tools.py`)
- `list_database_tables` - Explore database structure
- `get_table_schema` - View column definitions
- `query_database_table` - Retrieve data with filtering
- `insert_records` - Add new data
- `update_records` - Modify existing data
- `delete_records` - Remove data
- `execute_sql_query` - Run custom SELECT queries

### File Tools (`file_tools.py`)
- `list_files` - Browse storage contents
- `read_file` - Get file content
- `write_file` - Create or update files
- `delete_file` - Remove files or folders
- `copy_file` - Duplicate files
- `move_file` - Relocate or rename files
- `search_files` - Find files by name pattern

## Error Handling

The toolkit implements Arcade's error hierarchy for robust error handling:

- **RetryableToolError**: Temporary failures that can be retried
- **ContextRequiredToolError**: Missing configuration or permissions
- **ToolExecutionError**: Known, unrecoverable errors
- **FatalToolError**: Critical failures
- **UpstreamError**: External service issues

All tools include:
- Automatic retry logic for transient failures
- Service readiness polling after creation
- Detailed error messages with debugging hints
- Parameter validation

## Development

### Running Tests
```bash
# Run all tests
make test

# Generate coverage report
make coverage
```

### Code Quality
```bash
# Run linting and type checking
make check
```

### Building
```bash
# Clean and build
make clean-build
make build
```

## Best Practices

1. **Use `create_database_api_complete` for new setups** - It handles all configuration in one step
2. **Specify exact fields when querying** - Reduces data transfer and improves performance
3. **Use pagination for large datasets** - Prevents timeouts and memory issues
4. **Leverage filtering at the database level** - More efficient than client-side filtering
5. **Use appropriate access levels** - Follow principle of least privilege
6. **Handle binary files with base64 encoding** - Ensures proper transmission

## Security

- API keys are stored securely in Arcade Secrets
- Never commit credentials to version control
- Use role-based access control for fine-grained permissions
- Regularly rotate API keys
- SQL injection prevention through parameterized queries

## Troubleshooting

### Common Issues

**"Service not ready" warnings**
- Services may take a few seconds to initialize
- The toolkit automatically polls for readiness

**"Authentication failed" errors**
- Verify your API key has system-level permissions
- Check that the DreamFactory URL is correct

**"Resource not found" errors**
- Use `list_services()` to verify service names
- Ensure the database/table exists

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Arcade Documentation: https://docs.arcade.dev
- DreamFactory Documentation: https://www.dreamfactory.com/docs/
- Issues: https://github.com/yourusername/arcade-toolkit/issues