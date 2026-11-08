#!/usr/bin/env python3
"""Database-Hub - one entry point.

Scouting bots scan the newest-data catalog, the planner pairs findings
into inventions, the builder makes prototype specs, the tester runs
thousands of checks, and only passing creations deploy - to the sandbox
registry only. Real deployment, live scanning, satellite commands and
data-center access are HOLD gates.

Usage:
  python main.py                full pipeline + summary
  python main.py scan           scout findings only
  python main.py checks         self-checks
  python main.py --hold-demo    try a real deployment (held, exit 2)
  python main.py --deploy-sandbox  deploy passing creations to sandbox
"""
from __future__ import annotations

import sys

from database_hub import carbon4, deployer, flows, gates, pipeline, router, scouts, storage
from database_hub.catalog import DOMAINS, SOURCE_KINDS, build_catalog


def self_checks() -> tuple[int, int]:
    checks = []
    cat = build_catalog()
    checks.append(("catalog_36_records", len(cat) == 36))
    checks.append(("catalog_12_domains", sorted({r["domain"] for r in cat}) == sorted(DOMAINS)))
    checks.append(("catalog_3_source_kinds", sorted({r["source_kind"] for r in cat}) == sorted(SOURCE_KINDS)))
    checks.append(("catalog_all_offline", all(r["live"] is False for r in cat)))
    fleet = scouts.scout_fleet()
    checks.append(("scout_fleet_12_bots", len(fleet) == 12))
    findings = scouts.scan()
    checks.append(("scan_finds_all_fresh", len(findings) == 36))
    checks.append(("scan_ranked_desc", all(findings[i]["score"] >= findings[i + 1]["score"] for i in range(len(findings) - 1))))
    out = pipeline.run_pipeline()
    checks.append(("pipeline_12_plans", out["plans"] == 12))
    checks.append(("pipeline_3000_checks", out["total_checks"] == 3000))
    checks.append(("only_passing_deployed", out["deployed_sandbox"] == out["passed_prototypes"]))
    mesh = storage.full_mesh()
    checks.append(("clouds_17", len(mesh["clouds"]) == 17))
    checks.append(("sd_17_cards_x_1tb", len(mesh["sd_cards"]) == 17 and mesh["sd_total_tb"] == 17))
    checks.append(("google_drives_17", len(mesh["drives"]) == 17))
    checks.append(("storage_endpoints_51", mesh["endpoints"] == 51))
    checks.append(("storage_no_live_connections", mesh["live_connections"] == 0))
    placement = storage.place("INV-001")
    checks.append(("placement_3_copies", placement["copies"] == 3 and placement["sd"].startswith("SD-") and placement["drive"].startswith("DRIVE-") and placement["cloud"].startswith("CLOUD-")))
    hit = router.route("DATA-001", cached_on_sd=True)
    checks.append(("zero_network_latency_on_sd_hit", hit["zero_network_latency"] is True and hit["network_latency_ms"] == 0))
    miss = router.route("DATA-001", cached_on_sd=False)
    checks.append(("miss_uses_lowest_latency_cloud", miss["zero_network_latency"] is False and miss["network_latency_ms"] == 5))
    checks.append(("prefetch_uses_all_17_cards", pipeline.run_pipeline()["prefetch_cards_used"] == 17))
    checks.append(("carbon4_proceed_matches_deployed", out["carbon_proceed"] == out["deployed_sandbox"]))
    demo = carbon4.decide({"domains": ["energy", "space"], "kind": "sensor", "from": ["DATA-001", "DATA-019"], "pass_threshold": 0.90},
                          {"id": "PROTO-DEMO"}, {"verdict": "PASS", "pass_rate": 1.0}, target="production")
    checks.append(("carbon4_holds_production", demo["decision"] == "HOLD" and demo["live_call_made"] is False))
    checks.append(("carbon4_tiers", carbon4.TIERS == [2048, 8192, 32768] and carbon4.DEFAULT_TIER == 32768))
    fp = flows.merged_plan({"id": "INV-001", "domains": ["energy", "space"]})
    checks.append(("flows_all_4_used", fp["all_flows_used"] is True and fp["live_calls"] == 0))
    checks.append(("flowx_13_subtasks", flows.flowx_plan({"id": "INV-001"})["subtask_count"] == 13))
    checks.append(("filmmaking_not_rendered", flows.filmmaking_plan({"id": "INV-001"})["rendered"] is False))
    checks.append(("hold_gates_14", len(gates.HOLD_GATES) == 14))
    checks.append(("real_deployment_held", gates.is_held("real_deployment")))
    held = deployer.deploy({"id": "PROTO-X", "name": "x", "kind": "sensor"},
                           {"verdict": "PASS", "pass_rate": 1.0}, target="production")
    checks.append(("deploy_production_held", held["deployed"] is False and held["held"] is True))
    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return passed, len(checks)


def main(argv: list[str]) -> int:
    if "--hold-demo" in argv:
        held = deployer.deploy({"id": "PROTO-DEMO", "name": "demo", "kind": "sensor"},
                               {"verdict": "PASS", "pass_rate": 1.0}, target="production")
        print(f"HOLD: real_deployment gate - {held}")
        print("Nothing was deployed. Real deployment requires Darion's approval.")
        return 2
    if "checks" in argv:
        passed, total = self_checks()
        print(f"CHECKS {passed}/{total}")
        return 0 if passed == total else 1
    if "storage" in argv:
        mesh = storage.full_mesh()
        print("CLOUDS (17):")
        for c in mesh["clouds"]:
            print(f"  {c['id']} {c['name']:28s} {c['kind']:14s} model {c['latency_ms']} ms")
        print(f"SD CARDS (17): 17 x 1 TB = {mesh['sd_total_tb']} TB local edge")
        print("GOOGLE DRIVES (17): " + ", ".join(d["partition"] for d in mesh["drives"]))
        print(f"ENDPOINTS {mesh['endpoints']} - live connections: {mesh['live_connections']} (sync is a HOLD gate)")
        return 0
    if "scan" in argv:
        findings = scouts.scan()
        for f in findings:
            print(f"{f['bot']:12s} {f['id']} [{f['source_kind']}] {f['domain']:14s} score={f['score']}  {f['title']}")
        print(f"FINDINGS {len(findings)}")
        return 0
    out = pipeline.run_pipeline()
    print("Database-Hub pipeline: SCAN -> PLAN -> BUILD -> TEST -> DEPLOY (sandbox)")
    print(f"  findings scanned : {out['findings']}")
    print(f"  invention plans  : {out['plans']}")
    print(f"  prototypes built : {out['prototypes']}")
    print(f"  tests run        : {out['total_checks']} ({out['total_passed_checks']} passed)")
    print(f"  prototypes PASS  : {out['passed_prototypes']}")
    print(f"  deployed sandbox : {out['deployed_sandbox']} (successful creations only)")
    print(f"  storage mesh     : {out['storage_endpoints']} endpoints (17 clouds + 17 SD x 1 TB = {out['sd_total_tb']} TB + 17 Google Drives), prefetch on {out['prefetch_cards_used']} SD cards, zero network latency on SD hits")
    print(f"  carbon 4 decider : {out['carbon_proceed']} PROCEED (MAP->MODEL->STRESS->DECIDE, tier 32768 default, no live call)")
    print(f"  google flows     : all 4 used on every plan (FlowX 13 subtasks, Studio, Filmmaking rendered=False, DataX)")
    for r in out["results"]:
        d = "DEPLOYED sandbox" if r["deploy"]["deployed"] else "not deployed"
        print(f"  {r['plan']['id']} {r['plan']['name']:32s} pass_rate={r['test']['pass_rate']:.2f} {r['test']['verdict']} -> {d}")
    if "--deploy-sandbox" in argv:
        print(f"SANDBOX REGISTRY: {len(deployer.SANDBOX_REGISTRY)} creations")
    print("Real deployment: HOLD (gate: real_deployment)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
