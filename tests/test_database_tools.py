"""Test suite for DreamFactory Database Operations Tools."""

import pytest
from unittest.mock import MagicMock, patch
from arcade.sdk import ToolContext
from arcade.sdk.errors import RetryableToolError, ToolExecutionError

from arcade_dreamfactory.tools import database_tools


class TestDatabaseTools:
    """Test suite for database operations tools."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock tool context with secrets."""
        context = MagicMock(spec=ToolContext)
        context.get_secret.side_effect = lambda key: {
            "DREAM_FACTORY_BASE_URL": "https://example.com/api/v2",
            "DREAM_FACTORY_API_KEY": "test-api-key"
        }.get(key)
        return context

    @pytest.fixture
    def mock_request(self):
        """Mock the make_dreamfactory_request function."""
        with patch('arcade_dreamfactory.tools.database_tools.make_dreamfactory_request') as mock:
            yield mock

    def test_list_database_tables(self, mock_context, mock_request):
        """Test listing database tables."""
        mock_request.return_value = {
            "resource": [
                {"name": "users"},
                {"name": "products"},
                {"name": "orders"}
            ]
        }

        result = database_tools.list_database_tables(mock_context, "mysql_db")

        assert '"tables"' in result
        assert '"users"' in result
        assert '"products"' in result
        assert '"count": 3' in result
        mock_request.assert_called_once()

    def test_get_table_schema(self, mock_context, mock_request):
        """Test getting table schema."""
        mock_request.return_value = {
            "field": [
                {
                    "name": "id",
                    "type": "integer",
                    "db_type": "int",
                    "is_primary_key": True,
                    "auto_increment": True
                },
                {
                    "name": "email",
                    "type": "string",
                    "db_type": "varchar(255)",
                    "required": True
                }
            ]
        }

        result = database_tools.get_table_schema(mock_context, "mysql_db", "users")

        assert '"table": "users"' in result
        assert '"columns"' in result
        assert '"name": "id"' in result
        assert '"primary_key": true' in result
        mock_request.assert_called_once()

    def test_query_database_table(self, mock_context, mock_request):
        """Test querying database table."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "John", "email": "john@example.com"},
                {"id": 2, "name": "Jane", "email": "jane@example.com"}
            ]
        }

        result = database_tools.query_database_table(
            mock_context,
            service_name="mysql_db",
            table_name="users",
            filter="age > 25",
            limit=10
        )

        assert '"records"' in result
        assert '"count": 2' in result
        assert '"John"' in result
        assert '"Jane"' in result
        mock_request.assert_called_once()

    def test_query_database_table_with_fields(self, mock_context, mock_request):
        """Test querying with specific fields."""
        mock_request.return_value = {"resource": [{"id": 1}, {"id": 2}]}

        result = database_tools.query_database_table(
            mock_context,
            service_name="mysql_db",
            table_name="users",
            fields=["id", "name"]
        )

        assert '"records"' in result
        call_args = mock_request.call_args
        assert "fields" in call_args[1]['params']

    def test_get_records_by_ids(self, mock_context, mock_request):
        """Test getting records by IDs."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "Record 1"},
                {"id": 3, "name": "Record 3"}
            ]
        }

        result = database_tools.get_records_by_ids(
            mock_context,
            service_name="mysql_db",
            table_name="items",
            ids=[1, 2, 3]
        )

        assert '"requested_ids": [1, 2, 3]' in result
        assert '"found": 2' in result
        assert '"not_found": 1' in result
        mock_request.assert_called_once()

    def test_insert_records(self, mock_context, mock_request):
        """Test inserting records."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "New User", "email": "new@example.com"}
            ]
        }

        records = [{"name": "New User", "email": "new@example.com"}]
        result = database_tools.insert_records(
            mock_context,
            service_name="mysql_db",
            table_name="users",
            records=records
        )

        assert '"success": true' in result
        assert '"inserted_count": 1' in result
        assert "Successfully inserted" in result
        mock_request.assert_called_once()

    def test_update_records_with_filter(self, mock_context, mock_request):
        """Test updating records with filter."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "status": "inactive"},
                {"id": 2, "status": "inactive"}
            ]
        }

        result = database_tools.update_records(
            mock_context,
            service_name="mysql_db",
            table_name="users",
            updates={"status": "inactive"},
            filter="last_login < '2023-01-01'"
        )

        assert '"success": true' in result
        assert '"updates"' in result
        assert '"status": "inactive"' in result
        mock_request.assert_called_once()

    def test_update_records_with_ids(self, mock_context, mock_request):
        """Test updating records by IDs."""
        mock_request.return_value = {"resource": [{"id": 1, "price": 99.99}]}

        result = database_tools.update_records(
            mock_context,
            service_name="mysql_db",
            table_name="products",
            updates={"price": 99.99},
            ids=[1, 2, 3]
        )

        assert '"success": true' in result
        call_args = mock_request.call_args
        assert "filter" in call_args[1]['params']

    def test_update_records_no_identifier(self, mock_context):
        """Test updating records without filter or IDs."""
        with pytest.raises(RetryableToolError) as exc_info:
            database_tools.update_records(
                mock_context,
                service_name="mysql_db",
                table_name="users",
                updates={"status": "active"}
            )

        assert "Must provide either 'filter' or 'ids'" in str(exc_info.value)

    def test_delete_records_with_filter(self, mock_context, mock_request):
        """Test deleting records with filter."""
        mock_request.return_value = {"resource": []}

        result = database_tools.delete_records(
            mock_context,
            service_name="mysql_db",
            table_name="logs",
            filter="created_at < '2023-01-01'"
        )

        assert '"success": true' in result
        assert "Successfully deleted" in result
        mock_request.assert_called_once()

    def test_delete_records_with_ids(self, mock_context, mock_request):
        """Test deleting records by IDs."""
        mock_request.return_value = {"resource": []}

        result = database_tools.delete_records(
            mock_context,
            service_name="mysql_db",
            table_name="users",
            ids=[123, 456]
        )

        assert '"success": true' in result
        call_args = mock_request.call_args
        assert "filter" in call_args[1]['params']

    def test_execute_sql_query(self, mock_context, mock_request):
        """Test executing SQL query."""
        mock_request.return_value = {
            "resource": [
                {"count": 100}
            ]
        }

        result = database_tools.execute_sql_query(
            mock_context,
            service_name="mysql_db",
            sql="SELECT COUNT(*) as count FROM users"
        )

        assert '"results"' in result
        assert '"row_count": 1' in result
        mock_request.assert_called_once()

    def test_execute_sql_query_non_select(self, mock_context):
        """Test that non-SELECT queries are rejected."""
        with pytest.raises(ToolExecutionError) as exc_info:
            database_tools.execute_sql_query(
                mock_context,
                service_name="mysql_db",
                sql="DELETE FROM users"
            )

        assert "Only SELECT queries are allowed" in str(exc_info.value)

    def test_get_stored_procedures(self, mock_context, mock_request):
        """Test listing stored procedures."""
        mock_request.return_value = {
            "resource": [
                {"name": "calculate_totals"},
                {"name": "refresh_views"}
            ]
        }

        result = database_tools.get_stored_procedures(mock_context, "mysql_db")

        assert '"procedures"' in result
        assert '"count": 2' in result
        mock_request.assert_called_once()

    def test_call_stored_procedure(self, mock_context, mock_request):
        """Test calling stored procedure."""
        mock_request.return_value = {"result": "success", "rows_affected": 10}

        result = database_tools.call_stored_procedure(
            mock_context,
            service_name="mysql_db",
            procedure_name="update_stats",
            params={"user_id": 123}
        )

        assert '"procedure": "update_stats"' in result
        assert '"params"' in result
        assert '"result"' in result
        mock_request.assert_called_once()