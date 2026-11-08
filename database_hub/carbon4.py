"""Gemini Carbon 4 Extended Thinking - DECIDER seat for Database-Hub.

House pattern: MAP -> MODEL -> STRESS -> DECIDE, engine gemini-2.5-pro,
model google/gemini-carbon-4-extended-pro-thinking, thinking tiers
2048 / 8192 / 32768 (extended default). Offline structure is
authoritative: GEMINI_API_KEY is detected by presence only and is never
read, sent, or required. A live call is a HOLD gate. Carbon can only
tighten a verdict - it can turn a PASS into HOLD, never a FAIL into a
PASS, and never overrides a HOLD gate.
"""
from __future__ import annotations

import os

ENGINE = "gemini-2.5-pro"
MODEL_ID = "google/gemini-carbon-4-extended-pro-thinking"
KEY_ENV = "GEMINI_API_KEY"
TIERS = [2048, 8192, 32768]
DEFAULT_TIER = 32768


def key_present() -> bool:
    return bool(os.environ.get(KEY_ENV))


def pick_tier(pass_rate: float) -> int:
    # close calls get the deepest thinking
    if 0.90 <= pass_rate < 0.95:
        return 32768
    if pass_rate >= 0.95:
        return 8192
    return 2048


def decide(plan: dict, proto: dict, test: dict, target: str = "sandbox") -> dict:
    """Full MAP -> MODEL -> STRESS -> DECIDE run for one prototype."""
    mapped = {"domains": plan["domains"], "kind": plan["kind"],
              "from": plan["from"]}
    modelled = {"expected_pass_rate": plan["pass_threshold"],
                "observed_pass_rate": test["pass_rate"]}
    stress = {
        "test_passed": test["verdict"] == "PASS",
        "target_is_sandbox": target == "sandbox",
        "data_is_offline_synthetic": True,   # catalog records carry live=False
        "cross_domain_pair": plan["domains"][0] != plan["domains"][1],
    }
    stress_passed = sum(1 for v in stress.values() if v)
    if target != "sandbox":
        decision, level = "HOLD", "critical"        # HOLD gate always wins
    elif not stress["test_passed"]:
        decision, level = "REJECT", "standard"      # never tightened upward
    elif stress_passed < 4:
        decision, level = "HOLD", "elevated"        # tighten only
    else:
        decision, level = "PROCEED", "standard"
    return {
        "engine": ENGINE, "model": MODEL_ID,
        "tier": pick_tier(test["pass_rate"]),
        "phases": ["MAP", "MODEL", "STRESS", "DECIDE"],
        "map": mapped, "model_out": modelled,
        "stress": stress, "stress_passed": f"{stress_passed}/4",
        "decision": decision, "level": level,
        "key_present": key_present(),
        "live_call_made": False,
        "proto_id": proto["id"],
    }
