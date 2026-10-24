"""
End-to-end Pipeline Runner:
inbox.json -> (1) rule hints -> (2) Gemini classify (JSON schema)
           -> (3) merge by company+role -> (4) follow-up logic -> (5) UI Data

Also handles interview prep generation (stretch feature) and summary analytics.
"""
import os
import json
from typing import Dict, Any, List, Optional
from rule_hints import get_rule_hints
from gemini_classifier import classify_email
from tracker_merge import merge_and_track
from follow_up_logic import apply_follow_up_logic, DEFAULT_TODAY
from interview_prep import get_interview_prep


INBOX_PATH = os.path.join(os.path.dirname(__file__), "inbox.json")


def load_inbox(custom_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = custom_path or INBOX_PATH
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(
    inbox_data: Optional[List[Dict[str, Any]]] = None,
    today_str: str = DEFAULT_TODAY,
    api_key: Optional[str] = None,
    force_live: bool = False
) -> Dict[str, Any]:
    """
    Executes the full pipeline end-to-end:
    Returns complete dashboard payload.
    """
    emails = inbox_data if inbox_data is not None else load_inbox()
    classified_emails: List[Dict[str, Any]] = []

    cached_count = 0
    live_count = 0

    # Step 1 & 2: Rule hints & Gemini classification
    for item in emails:
        classification = classify_email(item, api_key=api_key, force_live=force_live)
        if classification.get("_from_cache"):
            cached_count += 1
        else:
            live_count += 1

        # Combine email metadata with classification
        combined = dict(item)
        combined.update(classification)
        classified_emails.append(combined)

    # Step 3: Merge applications & quarantine scams
    applications, scams = merge_and_track(classified_emails)

    # Step 4: Apply follow-up reminders
    applications = apply_follow_up_logic(applications, today_str=today_str)

    # Enrich interview-stage applications with interview prep notes (Stretch feature!)
    for app in applications:
        if app.get("status") == "interview":
            app["interview_prep"] = get_interview_prep(app.get("company", ""), app.get("role", ""))

    # Group applications by column for UI Kanban
    columns = {
        "applied": [a for a in applications if a.get("status") == "applied"],
        "interview": [a for a in applications if a.get("status") == "interview"],
        "offer": [a for a in applications if a.get("status") == "offer"],
        "rejected": [a for a in applications if a.get("status") == "rejected"]
    }

    # Calculate summary metrics
    follow_ups_due_count = sum(1 for a in applications if a.get("follow_up_due"))
    
    summary = {
        "total_emails_analyzed": len(emails),
        "scams_blocked": len(scams),
        "active_applications": len(applications),
        "follow_ups_due": follow_ups_due_count,
        "interview_count": len(columns["interview"]),
        "offer_count": len(columns["offer"]),
        "rejected_count": len(columns["rejected"]),
        "applied_count": len(columns["applied"]),
        "cached_responses": cached_count,
        "live_responses": live_count,
        "today_date": today_str
    }

    return {
        "summary": summary,
        "scams": scams,
        "columns": columns,
        "raw_emails": emails,
        "applications": applications
    }


if __name__ == "__main__":
    result = run_pipeline()
    print("Summary:", json.dumps(result["summary"], indent=2))
    print(f"Scams quarantined ({len(result['scams'])}):")
    for s in result["scams"]:
        print(f" - {s['company']} ({s['role']}): {s['scam_reasons']}")
    print(f"\nKanban Columns:")
    for col, items in result["columns"].items():
        print(f" - {col.upper()} ({len(items)}): {[x['company'] for x in items]}")
