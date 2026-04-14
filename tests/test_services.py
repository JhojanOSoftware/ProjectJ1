"""Unit tests for ArrendatarioService."""
import pytest
from unittest.mock import patch, Mock
from services.arrendatario_service import ArrendatarioService
from models.ClaseArrendatario import Arrendatario, ArrendatarioUpdate


class TestArrendatarioService:
    """Tests for ArrendatarioService methods."""
    
    @patch('utils.database.get_db_context')
    def test_get_all_arrendatarios(self, mock_db):
        """Test retrieving all arrendatarios."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "nombre_arrendatario": "Test User"}
        ]
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value.__enter__.return_value = mock_connection
        mock_db.return_value.__exit__.return_value = False
        
        result = ArrendatarioService.get_all_arrendatarios()
        
        assert len(result) == 1
        assert result[0]["id"] == 1
        mock_cursor.execute.assert_called_once()
    
    @patch('utils.database.get_db_context')
    def test_get_total_personas(self, mock_db):
        """Test calculating total people in a location."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"total": 5}
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value.__enter__.return_value = mock_connection
        mock_db.return_value.__exit__.return_value = False
        
        result = ArrendatarioService.get_total_personas("Test Location")
        
        assert result == 5
        mock_cursor.execute.assert_called_once()
    
    @patch('utils.database.get_db_context')
    def test_get_total_personas_empty(self, mock_db):
        """Test handling empty result for total personas."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"total": None}
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value.__enter__.return_value = mock_connection
        mock_db.return_value.__exit__.return_value = False
        
        result = ArrendatarioService.get_total_personas("Empty Location")
        
        assert result == 1  # Minimum value to avoid division by zero


class TestArrendatarioIntegration:
    """Integration tests for Arrendatario API."""
    
    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
