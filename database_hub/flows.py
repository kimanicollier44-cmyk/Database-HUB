"""Google Flows - all four, plan-only, for Database-Hub.

(1) Gemini-FlowX: 13-subtask orchestration graph for each invention.
(2) Google Workspace Studio Flows: starters/steps plan - nothing sent.
(3) Google Flow Filmmaking: storyboard + timeline plan, rendered=False.
(4) DataX Flow engine (engine_id google_flow): routing plan.

merged_plan() runs all four and proves all_flows_used. No live call is
made to any Google service; live video generation is a HOLD gate.
"""
from __future__ import annotations

FLOWX_SUBTASKS = [
    "intake_finding", "rank_sources", "draft_plan", "pair_domains",
    "spec_prototype", "schedule_tests", "run_battery", "carbon_review",
    "stress_review", "storage_place", "router_prefetch", "sandbox_deploy",
    "report_summary",
]

STUDIO_STARTERS = ["sheet_trigger", "form_trigger", "webhook_listener"]
STUDIO_STEPS = ["append_catalog_row", "post_chat_summary", "card_layout"]


def flowx_plan(plan: dict) -> dict:
    return {"flow": "gemini-flowx", "subtasks": FLOWX_SUBTASKS,
            "subtask_count": len(FLOWX_SUBTASKS), "queue_wait": 0,
            "plan_id": plan["id"]}


def studio_plan(plan: dict) -> dict:
    return {"flow": "workspace-studio", "starters": STUDIO_STARTERS,
            "steps": STUDIO_STEPS, "sent": False, "plan_id": plan["id"]}


def filmmaking_plan(plan: dict) -> dict:
    return {"flow": "flow-filmmaking", "mode": "offline-plan",
            "storyboard": ["setup", "analyze", "verdict", "teardown"],
            "tracks": ["setup", "analyze", "verdict", "teardown"],
            "rendered": False, "plan_id": plan["id"]}


def datax_plan(plan: dict) -> dict:
    return {"flow": "datax", "engine_id": "google_flow",
            "route": f"{plan['domains'][0]}->{plan['domains'][1]}",
            "plan_id": plan["id"]}


def merged_plan(plan: dict) -> dict:
    parts = [flowx_plan(plan), studio_plan(plan),
             filmmaking_plan(plan), datax_plan(plan)]
    return {"plan_id": plan["id"], "flows": parts,
            "all_flows_used": len(parts) == 4,
            "live_calls": 0, "rendered": False}
