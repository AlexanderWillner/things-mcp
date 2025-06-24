#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["things.py"]
# ///
"""
MCP (Model Context Protocol) server for Things 3 app integration.
Provides endpoints to get todos, projects, and add new todos to Things 3.
"""

import json
import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import things  # things.py library for Things 3 integration

# Default host - localhost for security
HOST = "127.0.0.1"


def find_available_port(start_port=9999):
    """
    Find the next available port starting from start_port.

    Args:
        start_port (int): Port to start checking from

    Returns:
        int: First available port found
    """
    port = start_port
    while True:
        try:
            # Try to bind to the port to check if it's available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, port))
                return port
        except OSError:
            # Port is in use, try the next one
            port += 1
            if port > 65535:
                raise RuntimeError("No available ports found")


# Handler functions for MCP methods
def handle_get_todos(params):
    """
    Retrieve todos from Things 3, optionally filtered by project and/or due date.

    Args:
        params (dict): Request parameters containing optional 'project_uuid' and 'due_date'

    Returns:
        list: List of todo items from Things 3
    """
    project = params.get("project_uuid")
    due_date = params.get("due_date")  # Expected format: 'YYYY-MM-DD'
    # Get todos for specific project or all todos if no project specified
    items = things.todos(project) if project else things.todos()
    if due_date:
        # Only include todos with a due date matching the requested date
        filtered = [todo for todo in items if todo.get("due_date") == due_date]
        return filtered
    return items


def handle_get_projects(_):
    """
    Retrieve all projects from Things 3.

    Args:
        _ (dict): Unused parameters (required for handler interface)

    Returns:
        list: List of all projects from Things 3
    """
    return things.projects()


# Map of method names to handler functions
HANDLERS = {
    "get-todos": handle_get_todos,
    "get-projects": handle_get_projects,
}


class MCPHandler(StreamRequestHandler):
    """
    Request handler for MCP protocol messages.
    Processes incoming JSON requests and routes them to appropriate handlers.
    """

    def handle(self):
        """Handle incoming MCP request."""
        # Read and parse JSON request from client
        data = json.loads(self.rfile.readline())
        method = data.get("method")
        params = data.get("params", {})

        # Route request to appropriate handler or return error
        if method not in HANDLERS:
            result = {"error": f"Unknown method: {method}"}
        else:
            try:
                result = HANDLERS[method](params)
            except Exception as e:
                result = {"error": str(e)}

        # Send JSON response back to client
        self.wfile.write(json.dumps(result).encode() + b"\n")


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """
    Multi-threaded TCP server for handling concurrent MCP requests.
    """

    daemon_threads = True  # Daemon threads exit when main program exits
    allow_reuse_address = (
        True  # Allow quick restart without "Address already in use" error
    )


def main():
    """
    Main server function - starts the MCP server on an available port.
    """
    # Find an available port starting from 9999
    port = find_available_port()

    # Start the threaded TCP server
    with ThreadedTCPServer((HOST, port), MCPHandler) as server:
        print(f"MCP server listening on {HOST}:{port}")
        print("Available methods: get-todos, get-projects")
        server.serve_forever()


if __name__ == "__main__":
    main()
