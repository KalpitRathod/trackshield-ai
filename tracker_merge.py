"""
Tracker Merge Module:
- Merges emails by canonical (company, role).
- State machine: applied (0) -> interview (1) -> offer (2); rejected is terminal.
- Scams are NEVER merged into applications; they are quarantined separately.
- Updates existing tracker rows when subsequent emails arrive (e.g. Applied -> Interview invite).
- Preserves full email audit timeline for each application.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime


STATUS_ORDER = {
    "applied": 1,
    "interview": 2,
    "offer": 3,
    "rejected": 4
}


def normalize_key(company: str, role: str) -> str:
    """Creates a normalized unique key for company and role."""
    comp = "".join(c for c in company.lower() if c.isalnum() or c.isspace()).strip()
    r = "".join(c for c in role.lower() if c.isalnum() or c.isspace()).strip()
    # Normalize common abbreviations
    comp = comp.replace("ltd", "").replace("pvt", "").replace("solutions", "").strip()
    return f"{comp}::{r}"


def merge_and_track(classified_emails: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Takes classified email objects and merges them into:
    1. applications: List of consolidated genuine applications
    2. scams: List of quarantined scam detections
    """
    applications_map: Dict[str, Dict[str, Any]] = {}
    scams: List[Dict[str, Any]] = []

    for item in classified_emails:
        status = item.get("status", "applied").lower()
        company = item.get("company", "Unknown")
        role = item.get("role", "Unknown Role")
        email_date = item.get("date", "2026-10-10")
        email_id = item.get("id")
        email_subject = item.get("subject", "")
        email_sender = item.get("from", "")
        email_body = item.get("body", "")
        interview_date = item.get("interview_date")
        scam_reasons = item.get("scam_reasons", [])
        confidence = item.get("confidence", 0.95)

        # 1. SCAMS NEVER MERGE INTO REAL APPLICATIONS
        if status == "scam":
            scams.append({
                "id": email_id,
                "company": company,
                "role": role,
                "status": "scam",
                "date": email_date,
                "from": email_sender,
                "subject": email_subject,
                "body": email_body,
                "scam_reasons": scam_reasons,
                "confidence": confidence
            })
            continue

        # 2. GENUINE APPLICATION MERGING
        key = normalize_key(company, role)
        email_event = {
            "email_id": email_id,
            "date": email_date,
            "subject": email_subject,
            "from": email_sender,
            "body": email_body,
            "status_signal": status
        }

        if key not in applications_map:
            applications_map[key] = {
                "key": key,
                "company": company,
                "role": role,
                "status": status,
                "first_date": email_date,
                "last_email_date": email_date,
                "interview_date": interview_date,
                "confidence": confidence,
                "timeline": [email_event],
                "email_count": 1
            }
        else:
            app = applications_map[key]
            app["timeline"].append(email_event)
            app["email_count"] += 1
            
            # Sort timeline by date
            app["timeline"].sort(key=lambda x: x["date"])
            app["last_email_date"] = app["timeline"][-1]["date"]
            app["first_date"] = app["timeline"][0]["date"]

            # State transition logic: status only moves forward
            current_status = app["status"]
            current_rank = STATUS_ORDER.get(current_status, 1)
            new_rank = STATUS_ORDER.get(status, 1)

            if status == "rejected":
                # Rejection overrides active pipeline states
                app["status"] = "rejected"
            elif new_rank > current_rank and current_status != "rejected":
                # Upgrade: applied -> interview -> offer
                app["status"] = status
            
            # Capture or update interview date if available
            if interview_date:
                app["interview_date"] = interview_date

    applications = list(applications_map.values())
    return applications, scams
