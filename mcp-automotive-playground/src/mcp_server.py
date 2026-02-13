"""Minimal MCP stdio server exposing automotive tools.

Implements a focused subset of MCP JSON-RPC methods used by this project:
- initialize
- notifications/initialized
- tools/list
- tools/call
"""

from __future__ import annotations

import json
import sys
from typing import Any

import services

PROTOCOL_VERSION = "2024-11-05"


TOOLS: dict[str, dict[str, Any]] = {
    "diagnostics": {
        "description": "Run diagnostics for a given OBD-II trouble code.",
        "inputSchema": {
            "type": "object",
            "properties": {"obd_code": {"type": "string"}},
            "required": [],
        },
    },
    "navigation": {
        "description": "Get route guidance for a destination.",
        "inputSchema": {
            "type": "object",
            "properties": {"destination": {"type": "string"}},
            "required": [],
        },
    },
    "weather": {
        "description": "Get weather conditions and risk for a region.",
        "inputSchema": {
            "type": "object",
            "properties": {"route_region": {"type": "string"}},
            "required": [],
        },
    },
    "maintenance": {
        "description": "Get maintenance recommendations based on mileage.",
        "inputSchema": {
            "type": "object",
            "properties": {"current_mileage": {"type": "integer"}},
            "required": [],
        },
    },
    "emergency": {
        "description": "Get emergency driving recommendation for a risk level.",
        "inputSchema": {
            "type": "object",
            "properties": {"risk_level": {"type": "string"}},
            "required": [],
        },
    },
    "knowledge": {
        "description": "Get automotive knowledge/explanation for a topic or code.",
        "inputSchema": {
            "type": "object",
            "properties": {"topic": {"type": "string"}},
            "required": [],
        },
    },
    "vehicle_info": {
        "description": "Get current vehicle profile details.",
        "inputSchema": {
            "type": "object",
            "properties": {"vin": {"type": "string"}},
            "required": [],
        },
    },
}


def _send(payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def _read_message() -> dict[str, Any] | None:
    content_length: int | None = None
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line == b"\r\n":
            break
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.split(b":", 1)[1].strip())
    if content_length is None:
        return None
    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8"))


def _tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "diagnostics":
        result = services.diagnostics(arguments.get("obd_code", "P0301"))
    elif name == "navigation":
        result = services.navigation(arguments.get("destination", "Office"))
    elif name == "weather":
        result = services.weather(arguments.get("route_region", "city"))
    elif name == "maintenance":
        result = services.maintenance(arguments.get("current_mileage", 42000))
    elif name == "emergency":
        result = services.emergency(arguments.get("risk_level", "low"))
    elif name == "knowledge":
        result = services.knowledge(arguments.get("topic", "P0301"))
    elif name == "vehicle_info":
        result = services.vehicle_info(arguments.get("vin", "DEMO-VIN-123"))
    else:
        raise ValueError(f"Unknown tool: {name}")

    return {"content": [{"type": "text", "text": json.dumps(result)}], "isError": False}


def main() -> None:
    while True:
        request = _read_message()
        if request is None:
            break

        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            if request_id is not None:
                _send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": PROTOCOL_VERSION,
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "automotive-playground", "version": "1.0.0"},
                        },
                    }
                )
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            if request_id is not None:
                tools = [
                    {"name": name, "description": spec["description"], "inputSchema": spec["inputSchema"]}
                    for name, spec in TOOLS.items()
                ]
                _send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
        elif method == "tools/call":
            params = request.get("params", {})
            try:
                result = _tool_call(params.get("name", ""), params.get("arguments", {}) or {})
                if request_id is not None:
                    _send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except Exception as exc:  # noqa: BLE001
                if request_id is not None:
                    _send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}})
        else:
            if request_id is not None:
                _send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"},
                    }
                )


if __name__ == "__main__":
    main()
