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


def flow(title: str, steps: list[tuple[str, str]]) -> dict:
    """An ordered set of who-does-what steps, drawn as a left-to-right diagram."""
    return {
        "kind": "flow",
        "title": title,
        "steps": [{"label": label, "detail": detail} for label, detail in steps],
    }


# The after-sales service flow, matching the org_business_flow document.
BUSINESS_FLOW_STEPS = [
    ("Clinic", "reports a fault"),
    ("Support", "opens the ticket"),
    ("Coordinator", "triages & dispatches"),
    ("Warehouse", "ships the spare part"),
    ("Technician", "repairs on-site"),
    ("Manager", "tracks cycle time"),
    ("Finance", "reconciles warranty"),
]


def business_flow_diagram() -> dict:
    """The full request-to-resolution flow, for questions about how work moves."""
    return flow("How a service request flows", BUSINESS_FLOW_STEPS)
