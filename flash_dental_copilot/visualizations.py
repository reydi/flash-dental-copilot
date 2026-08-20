"""Build compact visualization specs the demo front-end renders (bar, stat, flow).

Single responsibility: turn a computed result into a small, self-describing dict the
deck draws as a bar chart, a stat tile, or a flow diagram. Pure — no I/O, no model.
"""
from __future__ import annotations

from typing import Optional


def bar_chart(
    title: str, items: list[tuple[str, float]], unit: str = "", highlight: Optional[str] = None
) -> dict:
    """A ranked/broken-down set of labelled values, one bar each; one bar may be highlighted."""
    return {
        "kind": "bar",
        "title": title,
        "unit": unit,
        "highlight": highlight,
        "items": [{"label": label, "value": value} for label, value in items],
    }


def stat(title: str, value, unit: str = "", caption: str = "") -> dict:
    """A single headline number with a caption — for one-figure answers."""
    return {"kind": "stat", "title": title, "value": value, "unit": unit, "caption": caption}


def list_cards(title: str, items: list[tuple[str, str]]) -> dict:
    """A labelled list — each item a card with a heading and a sub-line (e.g. clinic + city)."""
    return {
        "kind": "list",
        "title": title,
        "items": [{"label": label, "sub": sub} for label, sub in items],
    }


def region_map(title: str, regions: list[dict]) -> dict:
    """A severity-coloured map of Indonesia's service regions — the front-end draws the map."""
    return {"kind": "map", "title": title, "regions": regions}


def flow(title: str, steps: list[tuple[str, str]]) -> dict:
    """An ordered set of who-does-what steps, drawn as a left-to-right diagram."""
    return {
        "kind": "flow",
        "title": title,
        "steps": [{"label": label, "detail": detail} for label, detail in steps],
    }


# The after-sales service flow — the seven steps from Flash Dental's own product brief.
BUSINESS_FLOW_STEPS = [
    ("Report in", "CS logs the ticket & picks the serial"),
    ("Triage", "asset profile, warranty & history shown"),
    ("Assign", "supervisor sets priority & technician"),
    ("Visit", "technician arrives & diagnoses"),
    ("Resolve", "action, spare part, photos, result"),
    ("Verify", "customer confirms, supervisor signs off"),
    ("Close", "ticket closed → asset history"),
]


def business_flow_diagram() -> dict:
    """The full request-to-resolution flow, for questions about how work moves."""
    return flow("How a service request flows", BUSINESS_FLOW_STEPS)
