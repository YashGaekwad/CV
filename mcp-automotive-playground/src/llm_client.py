"""MCP client with LLM-backed tool-calling loop (OpenAI Chat Completions).

Examples:
  python3 src/llm_client.py --list-tools
  OPENAI_API_KEY=... python3 src/llm_client.py --prompt "My check engine light is on"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.request
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SYSTEM_PROMPT = (
    "You are an automotive assistant. Use provided tools when needed, and return clear, safe advice."
)


class McpStdioClient:
    def __init__(self, server_cmd: str) -> None:
        self.proc = subprocess.Popen(
            [server_cmd, "src/mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._next_id = 1

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=2)

    def _send(self, payload: dict[str, Any]) -> None:
        if self.proc.stdin is None:
            raise RuntimeError("MCP server stdin unavailable")
        body = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self.proc.stdin.write(header)
        self.proc.stdin.write(body)
        self.proc.stdin.flush()

    def _read(self) -> dict[str, Any]:
        if self.proc.stdout is None:
            raise RuntimeError("MCP server stdout unavailable")

        content_length: int | None = None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("MCP server closed stdout")
            if line == b"\r\n":
                break
            if line.lower().startswith(b"content-length:"):
                content_length = int(line.split(b":", 1)[1].strip())

        if content_length is None:
            raise RuntimeError("Invalid MCP frame: missing Content-Length")

        body = self.proc.stdout.read(content_length)
        return json.loads(body.decode("utf-8"))

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        req_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)
        response = self._read()
        if "error" in response:
            raise RuntimeError(response["error"].get("message", "Unknown MCP error"))
        return response["result"]

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)


def _openai_chat(model: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


def list_tools(server_cmd: str) -> None:
    client = McpStdioClient(server_cmd)
    try:
        client.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": {"name": "local-cli", "version": "1.0.0"}})
        client.notify("notifications/initialized")
        tools = client.request("tools/list")["tools"]
        for tool in tools:
            print(f"- {tool['name']}: {tool.get('description', 'No description')}")
    finally:
        client.close()


def run_llm_flow(prompt: str, model: str, server_cmd: str) -> str:
    client = McpStdioClient(server_cmd)
    try:
        client.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": {"name": "local-cli", "version": "1.0.0"}})
        client.notify("notifications/initialized")
        mcp_tools = client.request("tools/list")["tools"]

        oa_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("inputSchema", {"type": "object", "properties": {}}),
                },
            }
            for t in mcp_tools
        ]

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        for _ in range(8):
            response = _openai_chat(model, messages, oa_tools)
            message = response["choices"][0]["message"]
            messages.append(message)

            tool_calls = message.get("tool_calls", [])
            if not tool_calls:
                return message.get("content", "") or ""

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                arguments = json.loads(tc["function"].get("arguments", "{}"))
                tool_result = client.request("tools/call", {"name": tool_name, "arguments": arguments})
                tool_text = ""
                for item in tool_result.get("content", []):
                    if item.get("type") == "text":
                        tool_text += item.get("text", "")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tool_name,
                        "content": tool_text,
                    }
                )

        return "Stopped after max tool-call iterations."
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP client with LLM-backed tool-calling")
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--prompt", help="User prompt")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    parser.add_argument("--server-cmd", default=os.getenv("PYTHON_BIN", "python3"))
    args = parser.parse_args()

    if args.list_tools:
        list_tools(args.server_cmd)
        return

    if not args.prompt:
        raise SystemExit("Provide --prompt or use --list-tools")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for --prompt mode")

    print(run_llm_flow(args.prompt, args.model, args.server_cmd))


if __name__ == "__main__":
    main()
