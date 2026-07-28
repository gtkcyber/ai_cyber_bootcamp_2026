"""Tool registry. Import this module to auto-register all reference tools."""

from .base import Tool, ToolRegistry, tool, REGISTRY
from . import http_tool, recon_tool  # noqa: F401  — register on import

__all__ = ["Tool", "ToolRegistry", "tool", "REGISTRY"]
