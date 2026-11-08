"""Newest-data catalog for Database-Hub.

Offline, deterministic, synthetic records that stand in for the feeds
scout bots would read live. Live fetching is a HOLD gate (see gates.py):
no record here came from a live site, a satellite, or a data center.

Each record: id, source_kind (data_center | satellite | ground_feed),
domain, title, novelty (0-100), usefulness (0-100), age_hours.
"""
from __future__ import annotations

DOMAINS = [
    "energy", "climate", "medicine", "robotics", "transport",
    "computing", "space", "agriculture", "water", "materials",
    "security", "communications",
]

SOURCE_KINDS = ["data_center", "satellite", "ground_feed"]

# (domain, title) seed findings - 36 records, 3 per domain
_SEEDS = [
    ("energy", "High-density battery cycling pattern"),
    ("energy", "Grid load spike prediction signal"),
    ("energy", "Waste-heat recapture efficiency curve"),
    ("climate", "Ocean surface temperature anomaly"),
    ("climate", "Methane plume detection snapshot"),
    ("climate", "Rainfall micro-forecast improvement"),
    ("medicine", "Plant compound extraction yield"),
    ("medicine", "Protein folding shortcut candidate"),
    ("medicine", "Wearable hydration signal correlation"),
    ("robotics", "Low-cost grip force calibration"),
    ("robotics", "Warehouse path collision pattern"),
    ("robotics", "Drone battery swap timing window"),
    ("transport", "Traffic flow compression model"),
    ("transport", "EV charging queue prediction"),
    ("transport", "Rail vibration early-warning signal"),
    ("computing", "Cache hit-rate anomaly pattern"),
    ("computing", "Small-model routing accuracy gain"),
    ("computing", "Data compression ratio breakthrough"),
    ("space", "Satellite debris conjunction warning"),
    ("space", "Low-orbit downlink window extension"),
    ("space", "Radiation-tolerant memory error rate"),
    ("agriculture", "Soil moisture satellite correlation"),
    ("agriculture", "Crop stress spectral signature"),
    ("agriculture", "Irrigation timing efficiency gain"),
    ("water", "Leak acoustic signature library"),
    ("water", "Desalination membrane fouling rate"),
    ("water", "River level forecast lead time"),
    ("materials", "Recycled alloy strength result"),
    ("materials", "Self-healing polymer test curve"),
    ("materials", "Graphene filter throughput record"),
    ("security", "Phishing pattern drift detection"),
    ("security", "Honeypot attack trend snapshot"),
    ("security", "Firmware anomaly fingerprint"),
    ("communications", "Mesh network relay hop reduction"),
    ("communications", "Signal denoising filter gain"),
    ("communications", "Underwater acoustic modem range"),
]


def build_catalog() -> list[dict]:
    records = []
    for i, (domain, title) in enumerate(_SEEDS):
        novelty = 55 + ((i * 37) % 45)          # 55..99 deterministic
        usefulness = 50 + ((i * 53) % 50)       # 50..99 deterministic
        records.append({
            "id": f"DATA-{i+1:03d}",
            "source_kind": SOURCE_KINDS[i % 3],
            "domain": domain,
            "title": title,
            "novelty": novelty,
            "usefulness": usefulness,
            "age_hours": (i * 7) % 72,          # 0..71h old = "newest" window
            "live": False,
        })
    return records
