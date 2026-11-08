"""Tester - runs thousands of deterministic checks per prototype.

Reference model: a prototype passes a check when a seeded pseudo-random
draw stays below its quality. The battery is honest - flawed prototypes
(quality < threshold) fail most checks and are rejected, never deployed.
"""
from __future__ import annotations

import hashlib


def _draw(seed: int, n: int) -> float:
    h = hashlib.sha256(f"{seed}:{n}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def run_battery(proto: dict, threshold: float = 0.90, checks: int = 250) -> dict:
    passed = sum(1 for i in range(checks) if _draw(proto["seed"], i) < proto["quality"])
    rate = passed / checks
    return {
        "proto_id": proto["id"],
        "checks": checks,
        "passed": passed,
        "pass_rate": round(rate, 4),
        "verdict": "PASS" if rate >= threshold else "FAIL",
    }
