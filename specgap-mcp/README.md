# SpecGap MCP Wrapper

A **local, deterministic stdio MCP server** that exposes bounded SpecGap operations for assurance pipelines, BoxArena pre-flight workflows, and reproducible evaluation.

## What this is

- A thin interoperability layer over existing SpecGap CLI logic
- Three tools: `analyze_spec`, `evaluate_candidates`, `boxarena_preflight`
- Synchronous tool execution, JSON summaries, Markdown report paths
- Composable with Claude Desktop, Cursor, Windsurf, CI scripts, or other MCP clients

## What this is NOT

- Not an autonomous agent or orchestration platform
- Not runtime verification or sandbox enforcement
- Not formal verification or semantic understanding
- Not an AI governance system
- Does not execute BoxArena
- Does not add intelligence beyond SpecGap’s existing extraction + structural diff + Z3 checks

## Assurance boundary

The MCP wrapper exposes **SpecGap tooling only**:

- It does **not** verify runtimes or containers
- It does **not** execute BoxArena or adversarial evaluation
- It does **not** provide autonomous assurance
- Outputs are bounded by **extracted constraints** and the **abstract sandbox model**
- A `no_divergence_detected` verdict means no divergence was found under that model — not correctness, not security

See also: [`docs/SPECIFICATION.md`](../docs/SPECIFICATION.md), [`docs/TCB.md`](../docs/TCB.md), [`docs/ENCODING.md`](../docs/ENCODING.md).

## Installation

From the SpecGap repository root (`specgap/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r specgap-mcp/requirements.txt
```

## Local usage

### Smoke test (no MCP client required)

```bash
cd specgap-mcp
python smoke_test.py
```

### Start stdio server

```bash
cd specgap-mcp
python server.py
```

The server speaks MCP over stdin/stdout. Launch it via an MCP client (below), not interactively.

## MCP tools

| Tool | Wraps | Primary outputs |
| --- | --- | --- |
| `analyze_spec` | Standard triple analysis | **`result`** (`AssuranceResult` envelope), `report_path` |
| `evaluate_candidates` | `--evaluate-candidates` | `candidate_outcomes`, `ordering`, `report_path` |
| `boxarena_preflight` | `--boxarena-preflight` | `preflight_verdict`, `proceed_to_boxarena_advisory`, `evidence_path` |

## Example MCP calls

Request (conceptual):

```json
{
  "tool": "analyze_spec",
  "arguments": {
    "input": "examples/sandbox_no_network.json"
  }
}
```

Response (abridged):

```json
{
  "tool": "analyze_spec",
  "report_path": ".../reports/mcp/analyze_sandbox_no_network.md",
  "result": {
    "assurance_result_schema": "1.0",
    "kind": "specgap",
    "producer": { "name": "specgap", "version": "0.1.0" },
    "input_fingerprint": "<64-char hex>",
    "verdict": "divergence_detected",
    "availability": { "verdict": "available", "input_fingerprint": "available" },
    "detail": { "specgap_detail_schema": "1.0", "triangulation": { "...": "..." } }
  }
}
```

### `analyze_spec` response shape (v0.1)

- **`result`** — canonical **`AssuranceResult`** envelope (`assurance_result_schema: "1.0"`, `kind: "specgap"`). Use this for new integrations.
- **Deprecated top-level aliases** (one version, then removed): `verdict`, `intent_empty`, `semantic_divergences`, `high_severity_divergences`, `failed_implication_checks`, `implication_checks_total`, `triangulation`, `triangulation_records`, `extractor`, `title`, `limitations`. These mirror fields from `result` / `result.detail` for backward compatibility.

Full JSON schemas: [`schemas/assurance-result-1.0.schema.json`](../schemas/assurance-result-1.0.schema.json), [`schemas/specgap-detail-1.0.schema.json`](../schemas/specgap-detail-1.0.schema.json).

Python API: `from specgap import analyze_structured`.

Triangulation disagreement example:

```json
{
  "tool": "analyze_spec",
  "arguments": {
    "input": "examples/06_triangulation_disagreement.json"
  }
}
```

Expected highlights: `"semantic_divergences": 0`, `"failed_implication_checks": 2`, `"triangulation": "disagree"`.

## Claude Desktop configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) and add (adjust paths):

```json
{
  "mcpServers": {
    "specgap": {
      "command": "/ABSOLUTE/PATH/TO/specgap/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/specgap/specgap-mcp/server.py"],
      "cwd": "/ABSOLUTE/PATH/TO/specgap/specgap-mcp"
    }
  }
}
```

Restart Claude Desktop. The three SpecGap tools should appear in the MCP tool list.

## Cursor / Windsurf configuration

Add to your MCP settings (path varies by product):

```json
{
  "mcpServers": {
    "specgap": {
      "command": "/ABSOLUTE/PATH/TO/specgap/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/specgap/specgap-mcp/server.py"],
      "cwd": "/ABSOLUTE/PATH/TO/specgap/specgap-mcp"
    }
  }
}
```

Use the workspace venv Python so `specgap` and `z3-solver` resolve.

## TCB scope

The MCP layer adds only:

- JSON serialization of existing SpecGap results
- Path resolution relative to the SpecGap repo root
- stdio MCP transport

It inherits SpecGap’s TCB: rule extraction vocabulary, `WEAKER_OF` lattice, abstract propositional model, Z3 satisfiability checks.

## Limitations

- **Local-only** — no cloud services in the wrapper (fuzzy mode may call Anthropic if you opt in and set `ANTHROPIC_API_KEY`; default `rule` mode is offline)
- **No caching, DB, or telemetry**
- **Paths** — `input` is resolved from the SpecGap repo root unless absolute
- **Reports** — default output under `reports/mcp/` when `output` is omitted

## License

Same as the parent SpecGap project.
