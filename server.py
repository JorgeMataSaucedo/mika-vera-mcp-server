"""mika-vera-mcp-server · MCP server pa' Mika Core + Vera.

Expone via Model Context Protocol:
- vera.ask                     · pregunta a Vera con audit trail (Sonnet 5 · guardián · SQL trace)
- vera.trace_summary           · resumen de últimas 24h queries anonimizadas
- mika.autoevolution.observe   · resumen operacional Mika Core (Capa 4)
- mika.autoevolution.pending   · pending proposals por tier
- mika.autoevolution.commits   · commits recientes con verify status

Instala:
    pip install fastmcp httpx pydantic

Corre:
    python server.py
    # → HTTP server en http://localhost:8765/mcp

Config Claude Desktop:
    {"mcpServers":{"mika-vera":{"command":"python","args":["path/to/server.py"]}}}

Config Claude Code:
    claude mcp add mika-vera stdio -- python path/to/server.py

Env vars requeridas:
    MIKA_VERA_ENDPOINT   · https://mika-core-app.<hash>.<region>.azurecontainerapps.io
    MIKA_VERA_TOKEN      · Bearer token para llamar Vera
    MIKA_SQL_CONN_STR    · connection string SQL Server pa' observability views (opcional)

Canon respetado:
- Cero cross-tenant memory (Vera es aislada por vertical)
- Failure taxonomy visible en trace_summary
- Guardian verdict propagado en cada respuesta
- Solo LEE del catalog Mika · nunca escribe

Licencia: MIT
Autor: Miguel Mata · https://mikatalab.com
"""

import os
from typing import Optional

import httpx
from fastmcp import FastMCP


VERA_ENDPOINT = os.environ.get("MIKA_VERA_ENDPOINT", "").rstrip("/")
VERA_TOKEN = os.environ.get("MIKA_VERA_TOKEN", "").strip()
SQL_CONN = os.environ.get("MIKA_SQL_CONN_STR", "").strip()


mcp = FastMCP(
    name="mika-vera-mcp",
    instructions=(
        "Servidor MCP para Mika Core + Vera · asistente audit-first para operadores "
        "de logística en México. Toda respuesta es trazable a una fila SQL. Zero "
        "cross-tenant memory. Guardián semántico filtra cada output. Failure "
        "taxonomy en tabla mlTrace anonimizada. Portfolio Mikata AI Lab 2027. "
        "https://mikatalab.com"
    ),
)


# ============================================================================
# TOOL 1 · vera.ask
# ============================================================================

@mcp.tool()
async def vera_ask(
    question: str,
    operator_id: int = 1,
    generate_audio: bool = False,
) -> dict:
    """Pregunta a Vera · asistente audit-first para operadores de flotilla.

    Vera contesta preguntas sobre pago, documentos, rendimiento, agenda y bonos.
    Cada respuesta trazable a una fila SQL. Guardián semántico filtra output.
    Zero cross-tenant memory by design. Canon: 'silencio honesto antes que
    ficción cómoda'.

    Args:
        question: Pregunta en español (ej: "¿cuándo vence mi licencia federal?")
        operator_id: ID del operador (default 1 · seed Miguel Mata en sandbox)
        generate_audio: Si True devuelve audio_b64 (voz Coral, +~1.5s latencia)

    Returns:
        dict con:
        - answer          · respuesta texto
        - category        · categoría detectada (docs · dinero · agenda · etc)
        - guardian_verdict· pass|hold|block
        - context_used    · tables consultadas
        - cost_usd        · costo USD del query
        - latency_ms      · latencia total
        - correlation_id  · UUID pa' cross-reference
        - audio_b64       · MP3 base64 (solo si generate_audio=True)
    """
    if not VERA_ENDPOINT:
        return {"error": "MIKA_VERA_ENDPOINT env var no configured"}
    if not VERA_TOKEN:
        return {"error": "MIKA_VERA_TOKEN env var no configured"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            f"{VERA_ENDPOINT}/mika-lab/vera/ask",
            headers={
                "Authorization": f"Bearer {VERA_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "question": question,
                "operator_id": operator_id,
                "generate_audio": generate_audio,
            },
        )
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "body": r.text[:200]}
        return r.json()


# ============================================================================
# TOOL 2 · vera.trace_summary
# ============================================================================

@mcp.tool()
async def vera_trace_summary(hours: int = 24) -> dict:
    """Resumen anonimizado de queries a Vera (últimas N horas).

    Retorna stats por categoría · guardian verdicts · error flags · latency ·
    cost · hallucination suspects. Sin PII · SHA256 operator hash. Este es el
    artefacto "failure taxonomy pública" que separa portfolio de engineering.

    Args:
        hours: Ventana de tiempo (default 24, max 168)

    Returns:
        dict con TotalQueries · pass/hold/block counts · errors · avg_latency ·
        total_cost · categories breakdown
    """
    if not VERA_ENDPOINT or not VERA_TOKEN:
        return {"error": "MIKA_VERA_ENDPOINT / MIKA_VERA_TOKEN no configured"}
    hours = max(1, min(hours, 168))
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{VERA_ENDPOINT}/mika-lab/vera/trace/summary",
            headers={"Authorization": f"Bearer {VERA_TOKEN}"},
            params={"hours": hours},
        )
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "body": r.text[:200]}
        return r.json()


# ============================================================================
# TOOL 3 · mika.autoevolution.observe
# ============================================================================

@mcp.tool()
async def mika_autoevolution_observe() -> dict:
    """Resumen operacional Mika Core últimas 24h (Capa 4 · autoevolución).

    Retorna JSON con stats de mlTrace: total queries, latency, cost, errors,
    hallucination counts + counts de AutoevoluProposal (pending, recent commits,
    rollbacks). Este es el input que Mika usa para proponer updates a su catalog.

    Returns:
        dict con TotalQueries24h · OverallAvgLatencyMs · TotalCost24hUsd ·
        PendingProposals · CommitsLast7d · RollbacksLast7d · CategoryStats · TopErrors
    """
    if not VERA_ENDPOINT or not VERA_TOKEN:
        return {"error": "MIKA_VERA_ENDPOINT / MIKA_VERA_TOKEN no configured"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{VERA_ENDPOINT}/mika-lab/autoevolution/observe",
            headers={"Authorization": f"Bearer {VERA_TOKEN}"},
        )
        if r.status_code == 404:
            return {"note": "endpoint /mika-lab/autoevolution/observe not exposed yet · call via direct SQL if needed"}
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "body": r.text[:200]}
        return r.json()


# ============================================================================
# TOOL 4 · mika.autoevolution.pending
# ============================================================================

@mcp.tool()
async def mika_autoevolution_pending() -> dict:
    """Pending proposals Capa 4 agrupadas por ApprovalTier.

    Retorna cuenta de PROPOSED por tier (TIER_LOW · TIER_MEDIUM · TIER_HIGH) con
    IDs de las proposals. Usa esto para saber qué necesita review humano antes
    de aprobar cambios al catalog Mika.

    Returns:
        dict con tiers · pending_count · oldest_pending_at · max_risk · pending_ids
    """
    if not VERA_ENDPOINT or not VERA_TOKEN:
        return {"error": "MIKA_VERA_ENDPOINT / MIKA_VERA_TOKEN no configured"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{VERA_ENDPOINT}/mika-lab/autoevolution/pending",
            headers={"Authorization": f"Bearer {VERA_TOKEN}"},
        )
        if r.status_code == 404:
            return {"note": "endpoint not exposed yet · pending server extension"}
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "body": r.text[:200]}
        return r.json()


# ============================================================================
# TOOL 5 · mika.autoevolution.commits
# ============================================================================

@mcp.tool()
async def mika_autoevolution_commits(limit: int = 10) -> dict:
    """Commits recientes aplicados a Mika Core catalog (Capa 4).

    Retorna top N commits con: baseline vs post PASS %, verify status,
    IsProtected flag, applied_by. Este es el registro auditable de cambios
    hechos por autoevolución.

    Args:
        limit: Max commits a retornar (default 10, max 100)

    Returns:
        list de commits con CommitId · TargetPath · AppliedAt · Applied by ·
        BaselinePct · PostPct · VerifyStatus · IsProtected · Rationale
    """
    limit = max(1, min(limit, 100))
    if not VERA_ENDPOINT or not VERA_TOKEN:
        return {"error": "MIKA_VERA_ENDPOINT / MIKA_VERA_TOKEN no configured"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{VERA_ENDPOINT}/mika-lab/autoevolution/commits",
            headers={"Authorization": f"Bearer {VERA_TOKEN}"},
            params={"limit": limit},
        )
        if r.status_code == 404:
            return {"note": "endpoint not exposed yet · pending server extension"}
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "body": r.text[:200]}
        return r.json()


# ============================================================================
# main
# ============================================================================

if __name__ == "__main__":
    # Default: stdio transport (Claude Desktop / Claude Code compatible)
    # Para HTTP transport: mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
    mcp.run()
