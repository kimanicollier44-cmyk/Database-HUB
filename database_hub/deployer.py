"""Deployer - successful creations only, sandbox registry only.

Real deployment is a HOLD gate. Passing prototypes are recorded in an
in-memory sandbox registry; nothing leaves this process.
"""
from __future__ import annotations

from .gates import is_held

SANDBOX_REGISTRY: list[dict] = []


def deploy(proto: dict, result: dict, target: str = "sandbox") -> dict:
    if target != "sandbox":
        if is_held("real_deployment"):
            return {"deployed": False, "held": True, "gate": "real_deployment",
                    "target": target, "proto_id": proto["id"]}
    if result["verdict"] != "PASS":
        return {"deployed": False, "held": False, "reason": "test_failed",
                "proto_id": proto["id"]}
    entry = {"proto_id": proto["id"], "name": proto["name"],
             "kind": proto["kind"], "pass_rate": result["pass_rate"],
             "registry": "sandbox"}
    SANDBOX_REGISTRY.append(entry)
    return {"deployed": True, "held": False, **entry}
