"""Scouting bots for Database-Hub.

12 named scout bots, one per domain. Each bot scans the catalog for its
domain, drops stale records (>72h), dedupes by title, and ranks what is
left by novelty + usefulness. Deterministic, offline, zero processes
are spawned against any live source - the catalog is synthetic.
"""
from __future__ import annotations

from .catalog import DOMAINS, build_catalog

BOT_NAMES = {
    "energy": "VoltScout", "climate": "TerraScout", "medicine": "VitaScout",
    "robotics": "MechScout", "transport": "VeloScout",
    "computing": "ByteScout", "space": "OrbitScout",
    "agriculture": "AgriScout", "water": "HydroScout",
    "materials": "MatScout", "security": "ShieldScout",
    "communications": "WaveScout",
}


def scout_fleet() -> list[dict]:
    return [{"bot": BOT_NAMES[d], "domain": d} for d in DOMAINS]


def scan(catalog: list[dict] | None = None) -> list[dict]:
    catalog = catalog if catalog is not None else build_catalog()
    findings, seen = [], set()
    for rec in catalog:
        if rec["age_hours"] > 72 or rec["title"] in seen:
            continue
        seen.add(rec["title"])
        score = rec["novelty"] + rec["usefulness"]
        findings.append({**rec, "bot": BOT_NAMES[rec["domain"]], "score": score})
    findings.sort(key=lambda r: (-r["score"], r["id"]))
    return findings
