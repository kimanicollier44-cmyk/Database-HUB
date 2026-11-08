"""Invention planner - pairs top findings into invention plans.

A plan combines two findings from different domains (cross-domain
inventions are where the new value is), states a hypothesis, the build
kind, and the exact test it must pass before anything is deployed.
"""
from __future__ import annotations

BUILD_KINDS = [
    "sensor", "filter", "compressor", "predictor",
    "optimizer", "monitor", "router", "extractor",
]


def plan_inventions(findings: list[dict], max_plans: int = 12) -> list[dict]:
    plans, used = [], set()
    top = findings[:24]
    for i, a in enumerate(top):
        if len(plans) >= max_plans:
            break
        for b in top[i + 1:]:
            if b["domain"] == a["domain"] or b["id"] in used:
                continue
            used.add(a["id"]); used.add(b["id"])
            kind = BUILD_KINDS[len(plans) % len(BUILD_KINDS)]
            plans.append({
                "id": f"INV-{len(plans)+1:03d}",
                "name": f"{a['domain'].title()}-{b['domain'].title()} {kind.title()}",
                "kind": kind,
                "from": [a["id"], b["id"]],
                "domains": [a["domain"], b["domain"]],
                "hypothesis": f"{a['title']} + {b['title']} -> better {kind}",
                "combined_score": a["score"] + b["score"],
                "pass_threshold": 0.90,
            })
            break
    return plans
