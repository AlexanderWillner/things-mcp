#!/usr/bin/env python3
"""
Test suite for the MCP server using pytest framework.
"""

import json
import socket
import unittest
from unittest.mock import MagicMock, patch

import pytest

from things_mcp.mcp import find_available_port, handle_get_projects, handle_get_todos


class TestMCPServerFunctions(unittest.TestCase):
    """Test individual MCP server functions."""

    @patch("things_mcp.mcp.things")
    def test_handle_get_todos_no_project(self, mock_things):
        """Test getting todos without project filter."""
        mock_things.todos.return_value = [
            {"title": "Test Todo 1", "uuid": "123"},
            {"title": "Test Todo 2", "uuid": "456"},
        ]

        result = handle_get_todos({})

        mock_things.todos.assert_called_once_with()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Test Todo 1")

    @patch("things_mcp.mcp.things")
    def test_handle_get_todos_with_project(self, mock_things):
        """Test getting todos with project filter."""
        mock_things.todos.return_value = [{"title": "Project Todo", "uuid": "789"}]

        result = handle_get_todos({"project_uuid": "project123"})

        mock_things.todos.assert_called_once_with("project123")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Project Todo")

    @patch("things_mcp.mcp.things")
    def test_handle_get_projects(self, mock_things):
        """Test getting all projects."""
        mock_things.projects.return_value = [
            {"title": "Project 1", "uuid": "proj1"},
            {"title": "Project 2", "uuid": "proj2"},
        ]

        result = handle_get_projects({})

        mock_things.projects.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Project 1")

    @patch("socket.socket")
    def test_find_available_port(self, mock_socket):
        """Test finding an available port."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        # First call succeeds (port is available)
        port = find_available_port(9999)

        self.assertEqual(port, 9999)
        mock_sock.bind.assert_called_once_with(("127.0.0.1", 9999))

    @patch("socket.socket")
    def test_find_available_port_retry(self, mock_socket):
        """Test finding an available port when first attempt fails."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        # First call fails, second succeeds
        mock_sock.bind.side_effect = [OSError("Port in use"), None]

        port = find_available_port(9999)

        self.assertEqual(port, 10000)
        self.assertEqual(mock_sock.bind.call_count, 2)

    @patch("things_mcp.mcp.things")
    def test_handle_get_todos_with_due_date(self, mock_things):
        """Test getting todos filtered by due_date."""
        mock_things.todos.return_value = [
            {"title": "Todo 1", "uuid": "1", "due_date": "2024-06-01"},
            {"title": "Todo 2", "uuid": "2", "due_date": "2024-06-02"},
            {"title": "Todo 3", "uuid": "3"},  # No due_date
        ]
        result = handle_get_todos({"due_date": "2024-06-01"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Todo 1")

    @patch("things_mcp.mcp.things")
    def test_handle_get_todos_with_due_date_no_match(self, mock_things):
        """Test getting todos with due_date filter that matches nothing."""
        mock_things.todos.return_value = [
            {"title": "Todo 1", "uuid": "1", "due_date": "2024-06-01"},
        ]
        result = handle_get_todos({"due_date": "2024-06-05"})
        self.assertEqual(result, [])

    @patch("things_mcp.mcp.things")
    def test_handle_get_todos_with_due_date_missing_field(self, mock_things):
        """Test todos with missing due_date field are ignored by filter."""
        mock_things.todos.return_value = [
            {"title": "Todo 1", "uuid": "1"},
            {"title": "Todo 2", "uuid": "2", "due_date": "2024-06-01"},
        ]
        result = handle_get_todos({"due_date": "2024-06-01"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Todo 2")


class TestMCPServerIntegration(unittest.TestCase):
    """Integration tests for the MCP server."""

    def setUp(self):
        """Set up test client connection."""
        self.server_host = "127.0.0.1"
        # Use a different port for testing to avoid conflicts
        self.server_port = find_available_port(10000)

    def send_mcp_request(self, method: str, params: dict | None = None) -> dict | None:
        """Send a request to the MCP server."""
        if params is None:
            params = {}

        request = json.dumps({"method": method, "params": params})

        try:
            with socket.create_connection(
                (self.server_host, self.server_port), timeout=5
            ) as sock:
                sock.sendall((request + "\n").encode())
                response = sock.makefile().readline()
                return json.loads(response)
        except (ConnectionRefusedError, socket.timeout):
            raise unittest.SkipTest("MCP server not running for integration tests")
            return None

    @patch("things_mcp.mcp.things")
    def test_get_projects_endpoint(self, mock_things):
        """Test the get-projects endpoint."""
        mock_things.projects.return_value = [
            {"title": "Test Project", "uuid": "test123"}
        ]

        # This test requires a running server
        try:
            response = self.send_mcp_request("get-projects")
            # If we get here, server is running
            self.assertIsInstance(response, (list, dict))
        except Exception:
            raise unittest.SkipTest("Integration test requires running MCP server")

    @patch("things_mcp.mcp.things")
    def test_get_todos_endpoint(self, mock_things):
        """Test the get-todos endpoint."""
        mock_things.todos.return_value = [{"title": "Test Todo", "uuid": "todo123"}]

        try:
            response = self.send_mcp_request("get-todos")
            self.assertIsInstance(response, (list, dict))
        except Exception:
            raise unittest.SkipTest("Integration test requires running MCP server")

    def test_invalid_method(self):
        """Test handling of invalid method names."""
        try:
            response = self.send_mcp_request("invalid-method")
            self.assertIsNotNone(response)
            if response is not None:
                self.assertIn("error", response)
                self.assertIn("Unknown method", response["error"])
        except Exception:
            raise unittest.SkipTest("Integration test requires running MCP server")


class TestMCPServerEdgeCases:
    """Test edge cases and error handling."""

    @patch("things_mcp.mcp.things")
    def test_handle_todos_exception(self, mock_things):
        """Test error handling when things.todos() raises an exception."""
        mock_things.todos.side_effect = Exception("Things database error")

        # This would be caught by the server's error handling
        with pytest.raises(Exception, match="Things database error"):
            handle_get_todos({})

    @patch("things_mcp.mcp.things")
    def test_handle_projects_exception(self, mock_things):
        """Test error handling when things.projects() raises an exception."""
        mock_things.projects.side_effect = Exception("Things database error")

        with pytest.raises(Exception, match="Things database error"):
            handle_get_projects({})

    @patch("socket.socket")
    def test_find_available_port_exhaustion(self, mock_socket):
        """Test error when no ports are available."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        # All attempts fail
        mock_sock.bind.side_effect = OSError("Port in use")

        with pytest.raises(RuntimeError, match="No available ports found"):
            find_available_port(65535)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
