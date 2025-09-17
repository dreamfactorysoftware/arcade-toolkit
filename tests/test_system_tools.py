"""Test suite for DreamFactory System Management Tools."""

import pytest
from unittest.mock import MagicMock, patch
from arcade.sdk import ToolContext
from arcade.sdk.errors import ContextRequiredToolError, ToolExecutionError, RetryableToolError

from arcade_dreamfactory.tools import system_tools


class TestSystemTools:
    """Test suite for system management tools."""

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
        with patch('arcade_dreamfactory.tools.system_tools.make_dreamfactory_request') as mock:
            yield mock

    def test_list_services(self, mock_context, mock_request):
        """Test listing services."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "mysql_db", "type": "mysql"},
                {"id": 2, "name": "local_storage", "type": "local"}
            ]
        }

        result = system_tools.list_services(mock_context)

        assert '"services"' in result
        assert '"mysql_db"' in result
        assert '"count": 2' in result
        mock_request.assert_called_once()

    def test_list_services_with_filter(self, mock_context, mock_request):
        """Test listing services with type filter."""
        mock_request.return_value = {"resource": [{"id": 1, "name": "mysql_db", "type": "mysql"}]}

        result = system_tools.list_services(mock_context, service_type="mysql")

        assert '"mysql_db"' in result
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['params'].get('filter') == 'type=mysql'

    def test_create_database_service(self, mock_context, mock_request):
        """Test creating a database service."""
        mock_request.return_value = {"id": 123}

        with patch('arcade_dreamfactory.tools.system_tools.wait_for_service_ready', return_value=True):
            result = system_tools.create_database_service(
                mock_context,
                name="test_db",
                database_type="mysql",
                host="localhost",
                database="testdb",
                username="user",
                password="pass"
            )

        assert '"service_id": 123' in result
        assert '"success": true' in result
        assert '"service_name": "test_db"' in result
        mock_request.assert_called_once()

    def test_create_role(self, mock_context, mock_request):
        """Test creating a role."""
        mock_request.return_value = {"id": 456}

        result = system_tools.create_role(
            mock_context,
            name="test_role",
            service_name="mysql_db",
            access_level="read"
        )

        assert '"role_id": 456' in result
        assert '"role_name": "test_role"' in result
        assert '"access_level": "read"' in result
        mock_request.assert_called_once()

    def test_create_role_invalid_access_level(self, mock_context):
        """Test creating a role with invalid access level."""
        with pytest.raises(RetryableToolError) as exc_info:
            system_tools.create_role(
                mock_context,
                name="test_role",
                service_name="mysql_db",
                access_level="invalid"
            )

        assert "Invalid access level" in str(exc_info.value)

    def test_create_app(self, mock_context, mock_request):
        """Test creating an app with API key."""
        # Mock role lookup
        mock_request.side_effect = [
            {"resource": [{"id": 789, "name": "test_role"}]},  # Role lookup
            {"id": 321, "api_key": "generated-api-key"}  # App creation
        ]

        result = system_tools.create_app(
            mock_context,
            name="test_app",
            role_name="test_role"
        )

        assert '"api_key": "generated-api-key"' in result
        assert '"app_name": "test_app"' in result
        assert '"role": "test_role"' in result
        assert mock_request.call_count == 2

    def test_create_app_role_not_found(self, mock_context, mock_request):
        """Test creating an app when role doesn't exist."""
        mock_request.return_value = {"resource": []}

        with pytest.raises(ToolExecutionError) as exc_info:
            system_tools.create_app(
                mock_context,
                name="test_app",
                role_name="nonexistent_role"
            )

        assert "Role 'nonexistent_role' not found" in str(exc_info.value)

    def test_create_database_api_complete(self, mock_context, mock_request):
        """Test complete database API setup."""
        mock_request.side_effect = [
            {"id": 100},  # Service creation
            {"id": 200},  # Role creation
            {"id": 300, "api_key": "complete-api-key"}  # App creation
        ]

        with patch('arcade_dreamfactory.tools.system_tools.wait_for_service_ready', return_value=True):
            result = system_tools.create_database_api_complete(
                mock_context,
                service_name="complete_db",
                database_type="postgresql",
                host="db.example.com",
                database="proddb",
                username="dbuser",
                password="dbpass"
            )

        assert '"success": true' in result
        assert '"api_key": "complete-api-key"' in result
        assert '"service_name": "complete_db"' in result
        assert mock_request.call_count == 3

    def test_delete_service(self, mock_context, mock_request):
        """Test deleting a service."""
        mock_request.return_value = {"success": True}

        result = system_tools.delete_service(mock_context, service_id=123)

        assert '"success": true' in result
        assert "deleted successfully" in result
        mock_request.assert_called_once()

    def test_list_roles(self, mock_context, mock_request):
        """Test listing roles."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "admin"},
                {"id": 2, "name": "user"}
            ]
        }

        result = system_tools.list_roles(mock_context)

        assert '"roles"' in result
        assert '"count": 2' in result
        mock_request.assert_called_once()

    def test_list_apps(self, mock_context, mock_request):
        """Test listing applications."""
        mock_request.return_value = {
            "resource": [
                {"id": 1, "name": "mobile_app"},
                {"id": 2, "name": "web_app"}
            ]
        }

        result = system_tools.list_apps(mock_context)

        assert '"apps"' in result
        assert '"count": 2' in result
        mock_request.assert_called_once()

    def test_get_service_details(self, mock_context, mock_request):
        """Test getting service details."""
        mock_request.return_value = {
            "id": 123,
            "name": "test_service",
            "type": "mysql",
            "config": {"host": "localhost"}
        }

        result = system_tools.get_service_details(mock_context, service_id=123)

        assert '"name": "test_service"' in result
        assert '"type": "mysql"' in result
        mock_request.assert_called_once()