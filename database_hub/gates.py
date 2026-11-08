"""HOLD gates - actions Database-Hub will never do on its own."""
from __future__ import annotations

HOLD_GATES = {
    "live_web_scan": "Scraping / scanning live websites without owner approval",
    "satellite_command": "Sending any command to a real satellite",
    "datacenter_access": "Accessing a real data center or private database",
    "collect_personal_data": "Collecting personal / private information",
    "scrape_paywalled": "Fetching paywalled or login-gated content",
    "real_deployment": "Deploying a creation to real production / real users",
    "live_hardware": "Controlling real robots, vehicles, drones or machines",
    "clinical_use": "Using any medical creation on a real person",
    "spend_real_funds": "Spending real money",
    "sign_live_transaction": "Signing a live blockchain / financial transaction",
    "live_cloud_sync": "Connecting or syncing to a real cloud storage account",
    "google_drive_access": "Accessing a real Google Drive account",
    "live_gemini_api_call": "Calling the live Gemini / Carbon API",
    "live_video_generation": "Rendering a real video with Google Flow",
}


def is_held(action: str) -> bool:
    return action in HOLD_GATES
