"""Connect to the external MCP tools server and expose its tools to the agent.

A single MCPClient is opened for the app's lifetime (its session must stay live
while the agent calls the tools) and reused across all per-conversation agents.
"""
from __future__ import annotations

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

_client = None
_tools = None


def get_remote_tools():
    """Return the remote MCP tools (list of Strands tool objects). Opens the client
    on first call and keeps it open. Returns [] if no MCP_TOOLS_URL is configured."""
    global _client, _tools
    if _tools is not None:
        return _tools
    url = get_settings().mcp_tools_url
    if not url:
        return []
    from mcp.client.streamable_http import streamablehttp_client
    from strands.tools.mcp import MCPClient

    client = MCPClient(lambda: streamablehttp_client(url))
    client.__enter__()  # keep the session open for the app lifetime
    _client = client
    _tools = client.list_tools_sync()
    logger.info("connected to MCP tools at %s: %s", url, [t.tool_name for t in _tools])
    return _tools


def shutdown():
    global _client, _tools
    if _client is not None:
        try:
            _client.__exit__(None, None, None)
        except Exception:  # best-effort close
            pass
    _client = None
    _tools = None
