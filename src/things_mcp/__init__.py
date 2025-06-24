"""
things-mcp: Model Context Protocol server for Things 3 app integration
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("things-mcp")
except PackageNotFoundError:
    __version__ = "unknown"

from .mcp import main

__all__ = ["main"]
