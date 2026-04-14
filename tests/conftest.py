"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    """Provide test client for API."""
    from main import app
    return TestClient(app)


@pytest.fixture
def db_mock():
    """Mock database connection."""
    with patch('utils.database.get_db_context') as mock_db:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value.__enter__.return_value = mock_connection
        mock_db.return_value.__exit__.return_value = False
        yield mock_db, mock_connection, mock_cursor
