"""
Comprehensive unit test suite for Job Hunt Autopilot & TrackShield AI.
Run with: pytest or python -m unittest discover tests
"""
import unittest
import os
import sys

# Ensure root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rule_hints import get_rule_hints
from tracker_merge import merge_and_track
from follow_up_logic import generate_follow_up_draft, apply_follow_up_logic
from cybercrime_report import generate_complaint_dossier
from interview_prep import get_interview_prep
from pipeline import run_pipeline, load_inbox


class TestJobHuntAutopilot(unittest.TestCase):
    """Test suite verifying core Job Hunt Autopilot logic and reliability."""

    def test_rule_hints_scam_detection(self):
        """Verify heuristic pre-screening catches fraudulent job offers."""
        scam_email = {
            "from": "hr.tcs.onboarding@gmail.com",
            "subject": "TCS Offer Letter - Pay 4999 Registration Fee",
            "body": "Congratulations! Pay Rs 4,999 refundable fee via UPI to hr@upi and submit Aadhaar card."
        }
        hints = get_rule_hints(scam_email)
        self.assertTrue(hints["has_scam_signals"])
        self.assertTrue(hints["is_freemail"])
        self.assertGreater(len(hints["hints"]), 0)

    def test_rule_hints_genuine_email(self):
        """Verify heuristic scanner does not flag genuine corporate communication."""
        legit_email = {
            "from": "recruiter@microsoft.com",
            "subject": "Interview Invitation: Senior Software Engineer",
            "body": "Hi Kalpit, We would love to invite you for a 45-minute technical discussion next week."
        }
        hints = get_rule_hints(legit_email)
        self.assertFalse(hints["has_scam_signals"])
        self.assertFalse(hints["is_freemail"])
        self.assertEqual(len(hints["hints"]), 0)

    def test_state_progression_and_scam_override(self):
        """Verify that scams are strictly quarantined and never pollute the tracker."""
        emails = [
            {
                "id": 1,
                "company": "Acme Corp",
                "role": "Frontend Dev",
                "status": "applied",
                "date": "2026-10-10",
                "confidence": 0.95,
                "scam_reasons": []
            },
            {
                "id": 2,
                "company": "Acme Corp",
                "role": "Frontend Dev",
                "status": "interview",
                "date": "2026-10-15",
                "confidence": 0.98,
                "scam_reasons": []
            },
            {
                "id": 3,
                "company": "Fake Scam Ltd",
                "role": "Data Entry",
                "status": "scam",
                "date": "2026-10-18",
                "confidence": 0.99,
                "scam_reasons": ["Fee demand via UPI"]
            }
        ]
        apps, scams = merge_and_track(emails)
        self.assertEqual(len(apps), 1)
        self.assertEqual(len(scams), 1)
        # Verify status progression applied -> interview
        self.assertEqual(apps[0]["status"], "interview")
        self.assertEqual(apps[0]["company"], "Acme Corp")
        self.assertEqual(scams[0]["company"], "Fake Scam Ltd")

    def test_follow_up_alarm_logic(self):
        """Verify autopilot identifies stalled applications after 7 days."""
        apps = [
            {
                "company": "Stripe",
                "role": "Backend Engineer",
                "status": "applied",
                "last_email_date": "2026-10-10"
            },
            {
                "company": "Netflix",
                "role": "Platform Engineer",
                "status": "applied",
                "last_email_date": "2026-10-22"
            }
        ]
        evaluated = apply_follow_up_logic(apps, today_str="2026-10-24")
        self.assertTrue(evaluated[0]["follow_up_due"])
        self.assertIsNotNone(evaluated[0]["follow_up_draft"])
        self.assertFalse(evaluated[1]["follow_up_due"])
        self.assertIsNone(evaluated[1]["follow_up_draft"])

    def test_follow_up_draft_generator(self):
        """Verify automated polite follow-up draft generation."""
        draft = generate_follow_up_draft("Stripe", "Backend Engineer", "2026-10-10")
        self.assertIn("Backend Engineer", draft["subject"])
        self.assertIn("Stripe", draft["body"])
        self.assertIn("2026-10-10", draft["body"])

    def test_interview_prep_copilot(self):
        """Verify dynamic generation of tailored interview preparation notes."""
        prep = get_interview_prep("Google", "Site Reliability Engineer")
        self.assertIn("company", prep)
        self.assertIn("role", prep)
        self.assertGreater(len(prep["tech_focus"]), 0)
        self.assertGreater(len(prep["key_questions"]), 0)
        self.assertGreater(len(prep["smart_questions_to_ask"]), 0)

    def test_cybercrime_dossier_generation(self):
        """Verify 1930 / cybercrime.gov.in complaint formatting."""
        scam_email = {
            "id": 99,
            "company": "Impersonator Inc",
            "role": "AI Engineer",
            "from": "bad-actor@gmail.com",
            "subject": "Urgent Security Deposit Required",
            "body": "Pay Rs 6,500 security deposit via UPI to fraud@okaxis to receive laptop kit."
        }
        dossier = generate_complaint_dossier(scam_email, scam_reasons=["Demands UPI transfer", "Freemail domain"])
        self.assertEqual(dossier["status"], "ready")
        self.assertIn("evidence", dossier)
        self.assertIn("complaint_text", dossier)
        self.assertIn("fraud@okaxis", dossier["complaint_text"])

    def test_end_to_end_pipeline_offline(self):
        """Verify full autopilot pipeline runs deterministically with cached data."""
        data = run_pipeline(today_str="2026-10-24", force_live=False)
        self.assertIn("summary", data)
        self.assertIn("columns", data)
        self.assertIn("scams", data)
        self.assertGreater(data["summary"]["total_emails_analyzed"], 0)
        self.assertGreaterEqual(data["summary"]["scams_blocked"], 1)


if __name__ == "__main__":
    unittest.main()
