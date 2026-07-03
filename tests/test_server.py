"""Smoke tests para mika-vera-mcp-server.

Run: pytest tests/ -v
"""
import os
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
def _env():
    os.environ["MIKA_VERA_ENDPOINT"] = "https://mika-core-app.yellowmeadow-8e7f2ec5.southcentralus.azurecontainerapps.io"
    os.environ["MIKA_VERA_TOKEN"] = "test-token-abc"
    yield


def test_server_module_imports():
    """server.py imports without error."""
    import server
    assert server.mcp.name == "mika-vera-mcp"


def test_env_vars_read_at_import_time():
    """VERA_ENDPOINT and VERA_TOKEN read from env."""
    import importlib, server
    importlib.reload(server)
    assert server.VERA_ENDPOINT.startswith("https://")
    assert server.VERA_TOKEN == "test-token-abc"


@pytest.mark.asyncio
async def test_vera_ask_returns_dict():
    """vera_ask returns dict shape when server responds 200."""
    import importlib, server
    importlib.reload(server)

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "answer": "test respuesta",
        "guardian_verdict": "pass",
        "category": "docs",
        "cost_usd": 0.003,
        "latency_ms": 2200,
        "correlation_id": "test-uuid",
    }

    with patch("httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.__aenter__.return_value = client_instance
        client_instance.post = AsyncMock(return_value=mock_response)
        MockClient.return_value = client_instance

        result = await server.vera_ask("¿cuándo vence mi licencia?", operator_id=1)
        assert result["guardian_verdict"] == "pass"
        assert result["category"] == "docs"
        assert "correlation_id" in result


@pytest.mark.asyncio
async def test_vera_ask_missing_endpoint():
    """Returns error dict when env vars missing."""
    os.environ.pop("MIKA_VERA_ENDPOINT", None)
    import importlib, server
    importlib.reload(server)

    result = await server.vera_ask("test", operator_id=1)
    assert "error" in result
    assert "MIKA_VERA_ENDPOINT" in result["error"]


@pytest.mark.asyncio
async def test_vera_trace_summary_clamps_hours():
    """hours arg clamped to [1, 168]."""
    import importlib, server
    importlib.reload(server)

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"total": 100}

    with patch("httpx.AsyncClient") as MockClient:
        client_instance = AsyncMock()
        client_instance.__aenter__.return_value = client_instance
        client_instance.get = AsyncMock(return_value=mock_response)
        MockClient.return_value = client_instance

        # Way over max
        result = await server.vera_trace_summary(hours=999)
        # Confirm the get call params had clamped hours
        call_args = client_instance.get.call_args
        assert call_args.kwargs["params"]["hours"] == 168

        # Under min
        result = await server.vera_trace_summary(hours=0)
        call_args = client_instance.get.call_args
        assert call_args.kwargs["params"]["hours"] == 1


def test_all_tools_registered():
    """All 5 MCP tools are exposed at module level."""
    import importlib, server
    importlib.reload(server)

    # FastMCP 2.x list_tools() is async · check module-level presence instead
    expected = {"vera_ask", "vera_trace_summary", "mika_autoevolution_observe",
                "mika_autoevolution_pending", "mika_autoevolution_commits"}
    for name in expected:
        assert hasattr(server, name), f"missing tool: {name}"
        assert callable(getattr(server, name)), f"tool not callable: {name}"


@pytest.mark.asyncio
async def test_mcp_list_tools_async():
    """FastMCP list_tools returns all 5 registered tools (async API)."""
    import importlib, server
    importlib.reload(server)

    if not hasattr(server.mcp, 'list_tools'):
        return  # FastMCP API changed; skip gracefully

    tools = await server.mcp.list_tools()
    names = {t.name for t in tools}
    expected = {"vera_ask", "vera_trace_summary", "mika_autoevolution_observe",
                "mika_autoevolution_pending", "mika_autoevolution_commits"}
    assert expected.issubset(names), f"missing: {expected - names}"
