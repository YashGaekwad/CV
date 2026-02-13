# MCP Automotive Playground

A hands-on project showing both:
- a deterministic scenario runner, and
- a **real MCP server/client flow** with an LLM-backed tool-calling loop.

## What is real vs mock here?

- `src/services.py` is still mocked business data (safe for local learning).
- `src/mcp_server.py` is a **real MCP server** exposing those services as MCP tools.
- `src/llm_client.py` is a **real MCP client** that connects to the server and lets an LLM call tools.

So the protocol/tool-calling loop is real MCP; the domain data source is demo data.

## Project structure

- `src/orchestrator.py` — deterministic demo scenarios (no LLM)
- `src/services.py` — mocked automotive service functions
- `src/mcp_server.py` — MCP tool server (stdio)
- `src/llm_client.py` — MCP client + OpenAI tool-calling loop
- `docs/scenarios.md` — scenario catalog

## Prerequisites

- Python 3.10+
- `pip`
- OpenAI API key for LLM mode (`OPENAI_API_KEY`)

Install dependencies:

```bash
cd mcp-automotive-playground
python3 -m pip install -r requirements.txt
```

## 1) Run deterministic demo (no LLM)

```bash
python3 src/orchestrator.py --scenario check_engine
```

## 2) Verify MCP server/client wiring

This command starts the client, boots the MCP server over stdio, and lists discovered tools:

```bash
python3 src/llm_client.py --list-tools
```

## 3) Run real LLM-backed MCP flow

```bash
export OPENAI_API_KEY="your_key_here"
python3 src/llm_client.py --prompt "My check engine light is on and I need to drive 50km. What should I do?"
```

Optional model override:

```bash
export OPENAI_MODEL="gpt-4o-mini"
```

## Notes

- If `OPENAI_API_KEY` is missing, `llm_client.py --prompt ...` exits with a clear error.
- Tool calls are chosen dynamically by the model via OpenAI function-calling + MCP `call_tool` execution.
