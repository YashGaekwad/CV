"""Simple MCP-style scenario orchestrator for automotive demo workflows."""

import argparse
import json
from typing import Callable

import services


ScenarioRunner = Callable[[], dict]


def run_check_engine() -> dict:
    diag = services.diagnostics("P0301")
    know = services.knowledge(diag["obd_code"])
    maint = services.maintenance(42000)
    return {
        "scenario": "check_engine",
        "tool_calls": [diag, know, maint],
        "summary": "Diagnosed check-engine issue with explanation and service plan.",
    }


def run_route_risk() -> dict:
    route = services.navigation("Airport")
    weather = services.weather("airport corridor")
    emergency = services.emergency(weather["risk_level"])
    return {
        "scenario": "route_risk",
        "tool_calls": [route, weather, emergency],
        "summary": "Generated route with weather-aware risk advisory and contingency guidance.",
    }


def run_pre_trip() -> dict:
    vehicle = services.vehicle_info()
    maint = services.maintenance(vehicle["mileage"])
    diag = services.diagnostics("P0101")
    return {
        "scenario": "pre_trip",
        "tool_calls": [vehicle, maint, diag],
        "summary": "Completed pre-trip readiness check using vehicle profile and diagnostics.",
    }


def run_safe_drive() -> dict:
    weather = services.weather("downtown")
    route = services.navigation("Home")
    emergency = services.emergency(weather["risk_level"])
    knowledge = services.knowledge(weather["condition"])
    return {
        "scenario": "safe_drive",
        "tool_calls": [weather, route, emergency, knowledge],
        "summary": "Produced safe-driving advice based on real-time environmental context.",
    }


SCENARIOS: dict[str, ScenarioRunner] = {
    "check_engine": run_check_engine,
    "route_risk": run_route_risk,
    "pre_trip": run_pre_trip,
    "safe_drive": run_safe_drive,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Automotive MCP playground orchestrator")
    parser.add_argument("--scenario", choices=SCENARIOS.keys(), required=True)
    args = parser.parse_args()

    result = SCENARIOS[args.scenario]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
