#!/usr/bin/env python3
"""SpecGap MCP server — stdio transport, synchronous tool execution.

Local deterministic wrapper around bounded SpecGap operations.
Not an agent framework, not runtime verification, not orchestration.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Ensure tools package resolves when launched as `python server.py`
_MCP_DIR = Path(__file__).resolve().parent
if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))

from tools import analyze_spec, boxarena_preflight, evaluate_candidates  # noqa: E402

SERVER_NAME = "specgap"
SERVER_VERSION = "0.1.0"

LIMITATIONS = (
    "Outputs are bounded by extracted constraints and the abstract sandbox model. "
    "Not runtime verification, not formal proof, not semantic understanding."
)

TOOLS: list[Tool] = [
    Tool(
        name="analyze_spec",
        description=(
            "Run SpecGap on a specification triple (intent / policy / implementation). "
            "Returns divergence counts, implication failures, triangulation, and a "
            "Markdown report path. Deterministic with extractor=rule. "
            + LIMITATIONS
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Path to spec JSON (relative to SpecGap repo root or absolute).",
                },
                "extractor": {
                    "type": "string",
                    "enum": ["rule", "fuzzy"],
                    "default": "rule",
                    "description": "Constraint extraction mode. Default rule is deterministic/offline.",
                },
                "output": {
                    "type": "string",
                    "description": "Optional Markdown report output path.",
                },
            },
            "required": ["input"],
        },
    ),
    Tool(
        name="evaluate_candidates",
        description=(
            "Evaluate multiple candidate policies against one stakeholder intent. "
            "Returns PASS/FAIL per candidate (implication failures over extracted "
            "constraints), mechanical ordering, and report path. Not a leaderboard. "
            + LIMITATIONS
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Path to candidate evaluation JSON input.",
                },
                "extractor": {
                    "type": "string",
                    "enum": ["rule", "fuzzy"],
                    "default": "rule",
                },
                "output": {
                    "type": "string",
                    "description": "Optional Markdown report output path.",
                },
            },
            "required": ["input"],
        },
    ),
    Tool(
        name="boxarena_preflight",
        description=(
            "SpecGap pre-flight before BoxArena empirical evaluation. "
            "Emits advisory proceed_to_boxarena and evidence JSON. "
            "Does NOT execute BoxArena or verify runtime confinement. "
            + LIMITATIONS
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Path to spec JSON with optional top-level boxarena block.",
                },
                "extractor": {
                    "type": "string",
                    "enum": ["rule", "fuzzy"],
                    "default": "rule",
                },
                "output": {
                    "type": "string",
                    "description": "Optional Markdown pre-flight report path.",
                },
                "evidence_out": {
                    "type": "string",
                    "description": "Optional JSON evidence-chain output path.",
                },
                "boxarena_quest": {"type": "string"},
                "boxarena_runtime": {"type": "string"},
                "boxarena_model": {"type": "string"},
                "boxarena_root": {"type": "string"},
            },
            "required": ["input"],
        },
    ),
]

server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


def _dispatch(name: str, arguments: dict) -> dict:
    """Synchronous tool dispatch — no background workers."""
    if name == "analyze_spec":
        return analyze_spec(
            input=arguments["input"],
            extractor=arguments.get("extractor", "rule"),
            output=arguments.get("output"),
        )
    if name == "evaluate_candidates":
        return evaluate_candidates(
            input=arguments["input"],
            extractor=arguments.get("extractor", "rule"),
            output=arguments.get("output"),
        )
    if name == "boxarena_preflight":
        return boxarena_preflight(
            input=arguments["input"],
            extractor=arguments.get("extractor", "rule"),
            output=arguments.get("output"),
            evidence_out=arguments.get("evidence_out"),
            boxarena_quest=arguments.get("boxarena_quest"),
            boxarena_runtime=arguments.get("boxarena_runtime"),
            boxarena_model=arguments.get("boxarena_model"),
            boxarena_root=arguments.get("boxarena_root"),
        )
    raise ValueError(f"unknown tool: {name}")


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if arguments is None:
        arguments = {}
    try:
        payload = _dispatch(name, arguments)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        payload = {
            "tool": name,
            "error": str(exc),
            "limitations": LIMITATIONS,
        }
    return [TextContent(type="text", text=json.dumps(payload, indent=2, sort_keys=True))]


async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(_main())
