# MCP Automotive Playground

A hands-on starter project for demonstrating how AI can route requests to automotive microservices through the Model Context Protocol (MCP).

## Goal

Help an automotive team learn:
- MCP fundamentals (tool registration, context exchange, routing)
- How an agent decides which microservice to call
- How real-time automotive logic can be composed across services

## Included microservices (modeled)

1. Diagnostics
2. Navigation
3. Weather
4. Maintenance
5. Emergency
6. Knowledge
7. Vehicle Info

This scaffold uses mocked service clients so the team can focus on orchestration design first, then swap in real MCP server calls.

## Project structure

- `src/orchestrator.py` — lightweight planner/router for demo scenarios
- `src/services.py` — mocked service functions representing the 7 Informant services
- `docs/scenarios.md` — scenario catalog and expected tool chains

## Quick start

```bash
python3 src/orchestrator.py --scenario check_engine
python3 src/orchestrator.py --scenario route_risk
python3 src/orchestrator.py --scenario pre_trip
python3 src/orchestrator.py --scenario safe_drive
```

## Suggested next steps

1. Replace mocks in `services.py` with real MCP client calls.
2. Add trace logging for every tool call (service, reason, latency).
3. Add policy guards (for emergency escalation and safe-driving constraints).
4. Add a simple API/CLI UI for interactive prompts.

## Training outcomes

By the end of phase 1, team members should be able to:
- Explain why the orchestrator selected each service.
- Extend the workflow with a new automotive service.
- Implement fallback behavior when one service is unavailable.
