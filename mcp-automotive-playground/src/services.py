"""Mock automotive microservices used by the playground orchestrator."""

from datetime import datetime


def diagnostics(obd_code: str = "P0301") -> dict:
    severity = "medium" if obd_code.startswith("P03") else "low"
    return {
        "service": "Diagnostics",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "obd_code": obd_code,
        "severity": severity,
        "summary": "Engine misfire detected on cylinder 1" if obd_code == "P0301" else "Generic diagnostic result",
    }


def navigation(destination: str = "Office") -> dict:
    return {
        "service": "Navigation",
        "destination": destination,
        "distance_km": 24,
        "eta_minutes": 38,
        "route_risk_zone": "moderate",
    }


def weather(route_region: str = "city") -> dict:
    return {
        "service": "Weather",
        "region": route_region,
        "condition": "heavy rain",
        "visibility": "reduced",
        "risk_level": "high",
    }


def maintenance(current_mileage: int = 42000) -> dict:
    overdue = ["brake fluid", "air filter"] if current_mileage > 40000 else []
    return {
        "service": "Maintenance",
        "mileage": current_mileage,
        "overdue_items": overdue,
        "recommended_window_days": 7 if overdue else 30,
    }


def emergency(risk_level: str = "low") -> dict:
    recommendation = (
        "Avoid travel and keep roadside assistance on standby"
        if risk_level in {"high", "severe"}
        else "Drive with caution and monitor conditions"
    )
    return {
        "service": "Emergency",
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


def knowledge(topic: str = "P0301") -> dict:
    explanation = {
        "P0301": "Misfire in cylinder 1 can impact fuel economy and emissions.",
        "heavy rain": "Reduced visibility and braking performance increase stopping distance.",
    }.get(topic, "General automotive guidance.")
    return {
        "service": "Knowledge",
        "topic": topic,
        "explanation": explanation,
    }


def vehicle_info(vin: str = "DEMO-VIN-123") -> dict:
    return {
        "service": "Vehicle Info",
        "vin": vin,
        "model": "Demo EV Sedan",
        "year": 2022,
        "mileage": 42000,
    }
