"""Storage mesh for Database-Hub: 17 clouds + 17 SD cards + 17 Google Drives.

Design/data only. Nothing connects to a real cloud, a real Drive, or a
real SD card - live sync is a HOLD gate. The mesh is the full-project
layout: every artifact is placed on 1 SD card (local edge), 1 Google
Drive (full-project copy) and 1 cloud (off-site copy), chosen
deterministically by hash, so any single loss is recoverable.
"""
from __future__ import annotations

import hashlib

# 17 clouds - name, class, modelled network latency (ms) for routing only
CLOUDS = [
    ("AWS S3", "object", 38), ("Google Cloud Storage", "object", 34),
    ("Azure Blob Storage", "object", 41), ("Cloudflare R2", "edge-object", 18),
    ("Backblaze B2", "object", 44), ("Wasabi", "object", 39),
    ("DigitalOcean Spaces", "object", 36), ("Oracle Cloud Storage", "object", 45),
    ("IBM Cloud Object Storage", "object", 47), ("Alibaba Cloud OSS", "object", 88),
    ("Tencent Cloud COS", "object", 92), ("Hetzner Object Storage", "object", 62),
    ("MinIO Self-Hosted", "self-hosted", 5), ("Storj", "decentralized", 55),
    ("Filecoin", "decentralized", 120), ("Arweave", "permanent", 140),
    ("IPFS", "decentralized", 70),
]

DRIVE_PARTITIONS = [
    "code", "data", "catalog", "inventions", "prototypes", "tests",
    "deployments", "docs", "media", "backups", "models", "logs",
    "configs", "exports", "archive", "shared", "full-project",
]

SD_CARD_TB = 1


def cloud_mesh() -> list[dict]:
    return [{"id": f"CLOUD-{i+1:02d}", "name": n, "kind": k, "latency_ms": ms}
            for i, (n, k, ms) in enumerate(CLOUDS)]


def sd_mesh() -> list[dict]:
    return [{"id": f"SD-{i+1:02d}", "capacity_tb": SD_CARD_TB, "kind": "local-edge"}
            for i in range(17)]


def drive_mesh() -> list[dict]:
    return [{"id": f"DRIVE-{i+1:02d}", "partition": p, "kind": "google-drive"}
            for i, p in enumerate(DRIVE_PARTITIONS)]


def full_mesh() -> dict:
    clouds, sds, drives = cloud_mesh(), sd_mesh(), drive_mesh()
    return {
        "clouds": clouds, "sd_cards": sds, "drives": drives,
        "endpoints": len(clouds) + len(sds) + len(drives),   # 51
        "sd_total_tb": sum(c["capacity_tb"] for c in sds),   # 17
        "live_connections": 0,
    }


def place(artifact: str) -> dict:
    """Deterministic 3-copy placement: 1 SD + 1 Drive + 1 cloud."""
    h = int(hashlib.sha256(artifact.encode()).hexdigest()[:8], 16)
    mesh = full_mesh()
    return {
        "artifact": artifact,
        "sd": mesh["sd_cards"][h % 17]["id"],
        "drive": mesh["drives"][(h // 17) % 17]["id"],
        "cloud": mesh["clouds"][(h // 289) % 17]["id"],
        "copies": 3,
    }
