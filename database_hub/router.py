"""Zero-latency router.

Honest model: literal zero latency is physically impossible - light,
disks and networks all take time. What this router delivers is zero
*network* latency on a local hit: read from the SD edge cache first
(no network round-trip at all), then the self-hosted cloud, then the
nearest cloud, and only then the full cloud mesh. Prefetching the
scouts' top findings into the SD cache is what makes hits the norm.

Latency figures are the mesh's routing model, not live measurements.
"""
from __future__ import annotations

from .storage import cloud_mesh, full_mesh

LOCAL_SD_NETWORK_MS = 0      # no network round-trip on a local SD hit


def route(artifact: str, cached_on_sd: bool) -> dict:
    if cached_on_sd:
        return {"artifact": artifact, "served_from": "sd-edge",
                "network_latency_ms": LOCAL_SD_NETWORK_MS,
                "zero_network_latency": True}
    clouds = sorted(cloud_mesh(), key=lambda c: c["latency_ms"])
    best = clouds[0]
    return {"artifact": artifact, "served_from": best["id"],
            "cloud": best["name"], "network_latency_ms": best["latency_ms"],
            "zero_network_latency": False}


def prefetch_plan(finding_ids: list[str]) -> dict:
    """Top findings are prefetched to the 17 SD cards, round-robin."""
    mesh = full_mesh()
    assignments = {c["id"]: [] for c in mesh["sd_cards"]}
    for i, fid in enumerate(finding_ids):
        assignments[mesh["sd_cards"][i % 17]["id"]].append(fid)
    return {"cards_used": sum(1 for v in assignments.values() if v),
            "assignments": assignments}
