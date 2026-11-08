import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database_hub import builder, carbon4, deployer, flows, gates, planner, router, scouts, storage, tester
from database_hub.catalog import build_catalog
from database_hub.pipeline import run_pipeline


def test_catalog_shape():
    cat = build_catalog()
    assert len(cat) == 36
    assert len({r["domain"] for r in cat}) == 12
    assert {r["source_kind"] for r in cat} == {"data_center", "satellite", "ground_feed"}
    assert all(r["live"] is False for r in cat)


def test_scout_fleet_and_scan():
    assert len(scouts.scout_fleet()) == 12
    findings = scouts.scan()
    assert len(findings) == 36
    assert findings[0]["score"] >= findings[-1]["score"]


def test_planner_cross_domain():
    plans = planner.plan_inventions(scouts.scan())
    assert len(plans) == 12
    assert all(p["domains"][0] != p["domains"][1] for p in plans)


def test_builder_deterministic():
    plan = planner.plan_inventions(scouts.scan())[0]
    assert builder.build(plan) == builder.build(plan)
    assert builder.build(plan)["executed"] is False


def test_tester_counts():
    proto = {"id": "PROTO-T", "seed": 123, "quality": 0.99}
    r = tester.run_battery(proto, checks=250)
    assert r["checks"] == 250 and 0 <= r["passed"] <= 250


def test_pipeline_thousands_of_tests():
    out = run_pipeline()
    assert out["total_checks"] == 3000
    assert out["deployed_sandbox"] == out["passed_prototypes"]


def test_failed_prototype_never_deploys():
    dep = deployer.deploy({"id": "P1", "name": "x", "kind": "sensor"},
                          {"verdict": "FAIL", "pass_rate": 0.1})
    assert dep["deployed"] is False


def test_real_deployment_is_held():
    assert gates.is_held("real_deployment")
    dep = deployer.deploy({"id": "P2", "name": "x", "kind": "sensor"},
                          {"verdict": "PASS", "pass_rate": 1.0}, target="production")
    assert dep["deployed"] is False and dep["held"] is True


def test_all_hold_gates_present():
    for gate in ["live_web_scan", "satellite_command", "datacenter_access",
                 "collect_personal_data", "real_deployment", "clinical_use",
                 "live_cloud_sync", "google_drive_access",
                 "live_gemini_api_call", "live_video_generation"]:
        assert gates.is_held(gate)
    assert len(gates.HOLD_GATES) == 14


def test_storage_mesh_17_17_17():
    mesh = storage.full_mesh()
    assert len(mesh["clouds"]) == 17
    assert len(mesh["sd_cards"]) == 17 and mesh["sd_total_tb"] == 17
    assert len(mesh["drives"]) == 17
    assert mesh["endpoints"] == 51 and mesh["live_connections"] == 0


def test_placement_three_kinds_deterministic():
    p = storage.place("INV-001")
    assert p == storage.place("INV-001") and p["copies"] == 3
    assert p["sd"].startswith("SD-") and p["drive"].startswith("DRIVE-")
    assert p["cloud"].startswith("CLOUD-")


def test_router_zero_network_latency_local_first():
    hit = router.route("DATA-001", cached_on_sd=True)
    assert hit["zero_network_latency"] is True and hit["network_latency_ms"] == 0
    miss = router.route("DATA-001", cached_on_sd=False)
    assert miss["zero_network_latency"] is False and miss["network_latency_ms"] == 5


def test_carbon4_decider():
    plan = {"domains": ["energy", "space"], "kind": "sensor",
            "from": ["DATA-001", "DATA-019"], "pass_threshold": 0.90}
    ok = carbon4.decide(plan, {"id": "P"}, {"verdict": "PASS", "pass_rate": 0.97})
    assert ok["decision"] == "PROCEED" and ok["stress_passed"] == "4/4"
    assert ok["live_call_made"] is False and ok["tier"] in carbon4.TIERS
    bad = carbon4.decide(plan, {"id": "P"}, {"verdict": "FAIL", "pass_rate": 0.5})
    assert bad["decision"] == "REJECT"  # Carbon never upgrades a FAIL
    held = carbon4.decide(plan, {"id": "P"}, {"verdict": "PASS", "pass_rate": 1.0},
                          target="production")
    assert held["decision"] == "HOLD"


def test_flows_all_four_plan_only():
    plan = {"id": "INV-001", "domains": ["energy", "space"]}
    m = flows.merged_plan(plan)
    assert m["all_flows_used"] is True and m["live_calls"] == 0
    assert flows.flowx_plan(plan)["subtask_count"] == 13
    assert flows.filmmaking_plan(plan)["rendered"] is False


def test_pipeline_carbon_and_flows():
    out = run_pipeline()
    assert out["carbon_proceed"] == out["deployed_sandbox"]
    assert out["flows_all_used"] is True


def test_prefetch_all_cards():
    plan = router.prefetch_plan([f"DATA-{i:03d}" for i in range(1, 18)])
    assert plan["cards_used"] == 17
