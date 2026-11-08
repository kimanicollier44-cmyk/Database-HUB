"""Builder - turns a plan into a prototype spec (data only).

No arbitrary code is generated or executed. A prototype is a closed-kind
spec with deterministic parameters derived from its plan score, which
the tester then verifies against an independent reference.
"""
from __future__ import annotations

import hashlib


def _seed_int(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def build(plan: dict) -> dict:
    seed = _seed_int(plan["id"] + plan["name"])
    # quality is deterministic: strong plans build clean, weak plans carry a flaw
    quality = 0.80 + (seed % 20) / 100.0        # 0.80 .. 0.99
    if plan["combined_score"] < 260:
        quality -= 0.12                          # weak input data -> flawed build
    return {
        "id": f"PROTO-{plan['id']}",
        "plan_id": plan["id"],
        "name": plan["name"],
        "kind": plan["kind"],
        "quality": round(quality, 4),
        "seed": seed,
        "executed": False,
    }
