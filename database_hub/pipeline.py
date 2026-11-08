"""Full pipeline: SCAN -> PLAN -> BUILD -> TEST -> DEPLOY (sandbox)."""
from __future__ import annotations

from . import builder, carbon4, deployer, flows, planner, router, scouts, storage, tester


def run_pipeline(checks_per_proto: int = 250) -> dict:
    findings = scouts.scan()
    mesh = storage.full_mesh()
    prefetch = router.prefetch_plan([f["id"] for f in findings[:17]])
    plans = planner.plan_inventions(findings)
    results, total_checks, total_passed = [], 0, 0
    for plan in plans:
        proto = builder.build(plan)
        result = tester.run_battery(proto, threshold=plan["pass_threshold"],
                                    checks=checks_per_proto)
        decision = carbon4.decide(plan, proto, result, target="sandbox")
        flow_plan = flows.merged_plan(plan)
        if decision["decision"] != "PROCEED":
            dep = {"deployed": False, "held": decision["decision"] == "HOLD",
                   "reason": f"carbon4_{decision['decision'].lower()}",
                   "proto_id": proto["id"]}
        else:
            dep = deployer.deploy(proto, result, target="sandbox")
        total_checks += result["checks"]
        total_passed += result["passed"]
        results.append({"plan": plan, "proto": proto, "test": result,
                        "carbon4": decision, "flows": flow_plan, "deploy": dep})
    deployed = [r for r in results if r["deploy"]["deployed"]]
    return {
        "findings": len(findings),
        "plans": len(plans),
        "prototypes": len(results),
        "total_checks": total_checks,
        "total_passed_checks": total_passed,
        "passed_prototypes": sum(1 for r in results if r["test"]["verdict"] == "PASS"),
        "deployed_sandbox": len(deployed),
        "storage_endpoints": mesh["endpoints"],
        "sd_total_tb": mesh["sd_total_tb"],
        "prefetch_cards_used": prefetch["cards_used"],
        "carbon_proceed": sum(1 for r in results if r["carbon4"]["decision"] == "PROCEED"),
        "flows_all_used": all(r["flows"]["all_flows_used"] for r in results),
        "results": results,
    }
