# mika-vera-mcp-server

**MCP server para [Mika Core](https://mikatalab.com/spec) + Vera** · asistente audit-first para operadores de logística en México.

Expone via [Model Context Protocol](https://modelcontextprotocol.io) las capacidades públicas de Mika:

- **`vera.ask`** · pregunta a Vera con audit trail · cada respuesta trazable a una fila SQL
- **`vera.trace_summary`** · resumen anonimizado de queries últimas 24h · **failure taxonomy pública**
- **`mika.autoevolution.observe`** · resumen operacional Mika Core (Capa 4)
- **`mika.autoevolution.pending`** · pending proposals por ApprovalTier
- **`mika.autoevolution.commits`** · commits recientes con verify status

> **Portfolio Mikata AI Lab 2027** · aplicando a Anthropic / Woven Toyota / Google Japan como Applied AI · Forward Deployed Engineer.
>
> Backend production en Azure Container Apps desde Q2 2026 · Claude Sonnet 5 · guardián semántico · 96% PASS en golden set 50 preguntas.

---

## Canon respetado

- **Zero cross-tenant memory** by design · cada vertical es instancia aislada
- **Failure taxonomy visible** · `mlTrace` con SHA256 operator hash · sin PII
- **Guardián semántico** filtra cada output antes de user
- **Solo lee del catalog Mika** · nunca escribe · MCP server es read-only wrapper
- **"Silencio honesto antes que ficción cómoda"** · Vera se niega a inventar canon inexistente

---

## Install

```bash
git clone https://github.com/JorgeMataSaucedo/mika-vera-mcp-server
cd mika-vera-mcp-server
pip install -r requirements.txt
```

## Config

```bash
export MIKA_VERA_ENDPOINT="https://mika-core-app.<hash>.<region>.azurecontainerapps.io"
export MIKA_VERA_TOKEN="<bearer-token>"
```

## Run local

```bash
python server.py
```

## Claude Desktop config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mika-vera": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "MIKA_VERA_ENDPOINT": "https://mika-core-app.<hash>.<region>.azurecontainerapps.io",
        "MIKA_VERA_TOKEN": "<bearer-token>"
      }
    }
  }
}
```

## Claude Code config

```bash
claude mcp add mika-vera stdio -- python /absolute/path/to/server.py
```

---

## Ejemplos de uso

Una vez conectado a Claude Desktop/Code:

**Pregúntale a Vera:**
```
Usa vera_ask para saber cuándo vence mi licencia federal
```

Vera responderá con guardian_verdict, cost, latency, y correlation_id trazable a mlTrace.

**Ve la failure taxonomy:**
```
Muéstrame el trace_summary de las últimas 24h
```

Retorna categorías, pass/hold/block counts, hallucination suspects.

**Observability Capa 4:**
```
¿Qué propuestas están pending en Mika autoevolución?
```

Retorna proposals por tier · TIER_HIGH necesitan approval explícito.

---

## Arquitectura

```
Cliente MCP (Claude Desktop / Code)
   ↓ stdio
mika-vera-mcp-server (este repo)
   ↓ HTTPS + Bearer token
Mika Core FastAPI · Azure Container Apps
   ↓ pyodbc
Azure SQL Serverless · schema ml* (multi-tenant)
```

---

## Roadmap

- [x] `vera.ask` · funcional live
- [x] `vera.trace_summary` · trace anonymized public
- [ ] `mika.autoevolution.*` · pending HTTP exposure de las views (Capa 4 completado 2026-07-03, HTTP endpoints en siguiente release)
- [ ] MCP resource type · exponer `mlTrace` como recurso browsable
- [ ] MCP prompt templates · pa' operator persona shortcuts

---

## Licencia

MIT · ver [LICENSE](LICENSE)

## Autor

**Miguel Mata** · [mikatalab.com](https://mikatalab.com) · [@miguelmata](https://x.com/miguelmata)

Construido en México · entre turnos de trabajo · con Esclerosis Múltiple en tratamiento Tysabri · aplicando a roles remote AI Engineer para 2027.

*Sábado: cero código. Building sustainably matters. La app funciona. Yo también.*

**Infraestructura: Mika · Mikata AI Lab 🎀**
