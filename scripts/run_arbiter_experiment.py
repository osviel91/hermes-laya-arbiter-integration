#!/usr/bin/env python3
"""Run a small, secret-safe Arbiter MCP experiment.

The script starts the official stdio bridge, calls the public MCP tools, and writes
only sanitized results. It never prints or persists the Bearer token.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PYTHON = os.environ.get(
    "HERMES_PYTHON",
    str(
        HERMES_HOME
        / "installs/f7cb996275eebbfa/environments/4a7daf34684e4377929ad87a3cbe4ed0/venv/bin/python"
    ),
)
BRIDGE = os.environ.get(
    "ARBITER_BRIDGE",
    str(HERMES_HOME / "arbiter/integrations/mcp/arbiter_mcp.py"),
)
OUTPUT = Path(__file__).parent.parent / "experiments" / "results.json"


def load_env_file() -> None:
    env_path = Path(os.environ.get("HERMES_ENV_FILE", HERMES_HOME / ".env"))
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "LAYA_API_KEY":
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            os.environ["LAYA_API_KEY"] = value
            return
    raise RuntimeError(f"LAYA_API_KEY not found in {env_path}")


def parameters() -> StdioServerParameters:
    load_env_file()
    return StdioServerParameters(
        command=PYTHON,
        args=[BRIDGE],
        env={
            "ARBITER_URL": os.environ.get("ARBITER_URL", "https://laya.osviel.duckdns.org"),
            "ARBITER_MODEL": os.environ.get("ARBITER_MODEL", "auto"),
            "ARBITER_API_KEY": os.environ["LAYA_API_KEY"],
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        },
    )


def jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return value


async def main() -> None:
    single_state = (
        "PostgreSQL was restarted after exceeding its memory limit. "
        "The API recovered automatically."
    )
    single_options = {
        "ignore": "No action required",
        "investigate": "Investigate root cause",
        "escalate": "Immediate human escalation",
    }
    cases = [
        {
            "id": "oom-operational-response",
            "tool": "arbiter_classify",
            "arguments": {
                "state": single_state,
                "instructions": "What action should be taken for this operational state?",
                "options": single_options,
            },
        },
        {
            "id": "spanish-severity",
            "tool": "arbiter_classify",
            "arguments": {
                "state": "El servicio ha sufrido tres reinicios por falta de memoria durante la última hora.",
                "instructions": "Clasifica la severidad operativa.",
                "options": {
                    "low": "Sin impacto relevante",
                    "medium": "Degradación recuperable",
                    "high": "Impacto repetido o riesgo de indisponibilidad",
                },
            },
        },
        {
            "id": "incident-check",
            "tool": "arbiter_check",
            "arguments": {
                "state": single_state,
                "instructions": "This incident requires human intervention.",
            },
        },
        {
            "id": "batched-incident-decisions",
            "tool": "arbiter_decide",
            "arguments": {
                "state": single_state,
                "questions": {
                    "severity": {
                        "type": "choice",
                        "instructions": "Classify operational severity.",
                        "criteria": {
                            "low": "No relevant impact",
                            "medium": "Recoverable degradation",
                            "high": "Repeated impact or outage risk",
                        },
                    },
                    "needs_human": {
                        "type": "noul",
                        "instructions": "This incident requires human intervention.",
                    },
                    "action": {
                        "type": "choice",
                        "instructions": "Choose the most appropriate response.",
                        "criteria": single_options,
                    },
                },
            },
        },
    ]

    results: list[dict[str, Any]] = []
    async with stdio_client(parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for case in cases:
                result = await session.call_tool(case["tool"], arguments=case["arguments"])
                results.append(
                    {
                        "id": case["id"],
                        "tool": case["tool"],
                        "content": jsonable(result.content),
                        "structured": jsonable(
                            getattr(result, "structuredContent", None)
                            or getattr(result, "structured_content", None)
                        ),
                    }
                )

    payload = {
        "date": "2026-09-27",
        "endpoint": "https://laya.osviel.duckdns.org",
        "model": "auto",
        "tools_discovered": [tool.name for tool in tools.tools],
        "results": results,
        "limitations": [
            "Small, illustrative sample; not a statistical evaluation.",
            "Latency includes the remote service and bridge path.",
            "Results should not be interpreted as authorization for risky actions.",
        ],
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"tools_discovered={len(payload['tools_discovered'])}")
    print(f"cases={len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
