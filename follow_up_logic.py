"""
Follow-Up Reminder & Automated Draft Generator.
Checks applications in 'applied' status against reference 'today' date.
Flags overdue applications (>= 7 days without reply) and generates polite follow-up drafts.
"""
from datetime import datetime, date
from typing import List, Dict, Any


DEFAULT_TODAY = "2026-10-24"


def parse_date(date_str: str) -> date:
    """Parse YYYY-MM-DD string to date object."""
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return datetime.strptime(DEFAULT_TODAY, "%Y-%m-%d").date()


def generate_follow_up_draft(company: str, role: str, application_date: str) -> Dict[str, str]:
    """Generates a professional, thoughtful follow-up email template."""
    subject = f"Following up on application: {role} - Alex Chen"
    body = f"""Hi {company} Hiring Team,

I hope you are having a productive week.

I wanted to kindly follow up on the {role} position I applied for on {application_date}. I remain very enthusiastic about {company}'s engineering mission and would love to know if there are any updates regarding my candidacy.

Please let me know if you need any additional portfolio samples, references, or code repositories from my end.

Thank you for your time and consideration!

Warm regards,
Alex Chen
GitHub: github.com/alexchen-dev
Portfolio: alexchen.dev
LinkedIn: linkedin.com/in/alexchen-eng"""
    return {
        "subject": subject,
        "body": body
    }


def apply_follow_up_logic(applications: List[Dict[str, Any]], today_str: str = DEFAULT_TODAY) -> List[Dict[str, Any]]:
    """
    Evaluates follow-up status for all applications.
    If status == 'applied' and (today - last_email_date) >= 7 days:
        follow_up_due = True
    """
    today = parse_date(today_str)

    for app in applications:
        status = app.get("status")
        last_date = parse_date(app.get("last_email_date", today_str))
        days_passed = (today - last_date).days

        app["days_since_last_email"] = max(0, days_passed)

        if status == "applied" and days_passed >= 7:
            app["follow_up_due"] = True
            app["follow_up_reason"] = f"No response in {days_passed} days (threshold is 7 days)"
            app["follow_up_draft"] = generate_follow_up_draft(
                app.get("company", "the"),
                app.get("role", "Engineer"),
                app.get("first_date", app.get("last_email_date", today_str))
            )
        else:
            app["follow_up_due"] = False
            app["follow_up_reason"] = None
            app["follow_up_draft"] = None

    return applications
