# Changelog

## [1.0.0] - 2026-07-03

### Added
- Initial MCP server implementation with 5 tools:
  - `vera_ask` · query Vera with guardian verdict + SQL trace
  - `vera_trace_summary` · anonymized 24h stats (failure taxonomy public)
  - `mika_autoevolution_observe` · Capa 4 operational summary
  - `mika_autoevolution_pending` · pending proposals by ApprovalTier
  - `mika_autoevolution_commits` · recent commits with verify status
- README with install instructions for Claude Desktop + Claude Code
- MIT LICENSE
- `.gitignore` for Python
- `requirements.txt` with `fastmcp`, `httpx`, `pydantic`
- Smoke tests in `tests/test_server.py`
- GitHub Actions CI for Python 3.11 + 3.12

### Canon
- Zero cross-tenant memory by design
- Guardian semantic filter on every response
- Failure taxonomy (`mlTrace`) visible via `vera_trace_summary`
- Read-only wrapper · never writes to Mika Core catalog

## [Unreleased]

### Planned
- MCP resource type · expose `mlTrace` as browsable resource
- MCP prompt templates for operator persona shortcuts
- HTTP transport option (streamable-http) for remote hosting
