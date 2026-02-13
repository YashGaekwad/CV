# CV

This repository contains two runnable parts:

1. **Personal CV website** (static HTML/CSS at the repo root)
2. **MCP Automotive Playground** (Python CLI + MCP demo under `mcp-automotive-playground/`)

## Important clarification: real MCP vs demo/mimic

The automotive module now has both modes:

- **Deterministic demo mode** (`src/orchestrator.py`): local scripted scenario flow.
- **Real MCP flow** (`src/mcp_server.py` + `src/llm_client.py`): actual MCP server/client interaction with LLM tool-calling.

The service data itself (`src/services.py`) remains mocked sample data, but the MCP protocol and tool-calling loop are real.

## Prerequisites

- **Git**
- **Python 3.10+**
- Browser (for CV website)
- For LLM flow only: **OpenAI API key**

## 1) Run the CV website locally

```bash
cd /path/to/CV
python3 -m http.server 8000
```

Open:
- `http://127.0.0.1:8000/`
- `http://localhost:8000/`

## 2) Run MCP Automotive Playground

Install dependencies:

```bash
cd mcp-automotive-playground
python3 -m pip install -r requirements.txt
```

Deterministic scenario:

```bash
python3 src/orchestrator.py --scenario check_engine
```

List MCP tools (verifies real MCP server/client wiring):

```bash
python3 src/llm_client.py --list-tools
```

LLM-backed tool-calling flow:

```bash
export OPENAI_API_KEY="your_key_here"
python3 src/llm_client.py --prompt "My check engine light is on. What should I do?"
```

## Verified in this environment

- `python3 mcp-automotive-playground/src/orchestrator.py --scenario check_engine`
- `python3 mcp-automotive-playground/src/llm_client.py --list-tools`
