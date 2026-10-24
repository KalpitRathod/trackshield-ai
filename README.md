# 🛡️ TrackShield AI • GDG Garbathon 2026
### AI-Era Layoff Recovery Suite: Automated Kanban Tracker, Scam Quarantine, Follow-Up Alarms & Interview Prep Copilot

[![Repository Size](https://img.shields.io/badge/Repo%20Size-%3C%201%20MB%20(Rule%20Compliant)-brightgreen)](#important-rules-compliance)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)](#prerequisites)
[![AI Platform](https://img.shields.io/badge/Gemini%202.5%20Flash-Structured%20JSON-purple)](#architecture-and-approach)
[![License](https://img.shields.io/badge/License-MIT-teal)](LICENSE)

---

## 📌 1. Chosen Challenge Vertical

* **Challenge Persona:** A recently laid-off job seeker in the AI era who has applied to 100+ roles across job boards and career pages.
* **The Problem:** 
  1. **Application Chaos:** Applicants rapidly lose track of who responded, who rejected them, what stage each role is in, and when it is time to follow up.
  2. **Predatory Job Scams:** Vulnerable candidates are prime targets for fake job offers demanding "training fees" or "gate pass security deposits", harvesting unencrypted Aadhaar/PAN cards before any interview, or posing as enterprise companies from freemail/typosquatted domains.
* **The Solution (TrackShield AI):** An intelligent, deterministic and generative pipeline that ingests raw job-seeker emails, isolates fake offers into a quarantined Scam Shield, merges multi-touch communications into an self-updating 4-column Kanban tracker, flags stale applications with automated follow-up drafts, and prepares tailored interview briefing notes for upcoming rounds.

---

## 🚀 2. Quickstart & Local Setup

### Prerequisites
* Python 3.10 or higher
* Git installed and configured
* (Optional) Google Gemini API Key (offline fallback is included via Rule 06 disk cache)

### Installation & Run
```bash
# 1. Clone the public repository
git clone <YOUR_PUBLIC_REPO_URL>
cd "GDG Garbathon"

# 2. (Optional) Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate

# 3. Install lightweight dependencies
pip install fastapi uvicorn google-genai python-dotenv

# 4. (Optional) Configure Gemini API Key
# Create a .env file:
# GEMINI_API_KEY=your_gemini_api_key_here
# Note: Even without an API key, the system runs with 100% functionality using pre-cached responses!

# 5. Launch the application
python server.py
```
Open **`http://127.0.0.1:8000`** in any modern web browser.

---

## 💡 3. Approach and Logic

Rather than training a noisy, fragile machine learning model on job-posting datasets, our approach combines **deterministic pre-heuristics** with **Google Gemini 2.5 Flash structured reasoning** and **canonical state machines**:

### A. Heuristics & Rule Hints (`rule_hints.py`)
Deterministic regex patterns scan raw email headers and text for instant, high-confidence red flags before LLM invocation:
* Upfront fee demands (e.g., *₹3,999 training fee*, *₹6,500 refundable security deposit via UPI/IMPS*).
* Identity document harvesting (*Aadhaar*, *PAN*, *cancelled cheque* demanded via reply before any interview).
* Freemail sender impersonation (e.g., enterprise company like Infosys emailing from `@gmail.com`).
* Lookalike/typosquatted domains (e.g., `techmahindra-careers.co`, `tcs-careers-portal.com`).
* Off-platform chat diverts (e.g., Telegram handle redirects for interviews).

### B. Gemini 2.5 Flash Structured Classification (`gemini_classifier.py`)
Gemini processes the email alongside rule hints and returns strict JSON following a Pydantic-style schema:
* `company`: Canonical employer name.
* `role`: Job title.
* `status`: `applied` | `interview` | `offer` | `rejected` | `scam`.
* `scam_reasons`: Array of human-readable justifications explaining why the email was quarantined.
* `confidence`: Float confidence score.
* `interview_date`: ISO date string (if interview invitation).

> **CRITICAL LAW — SCAM OVERRIDES EVERYTHING:** If an email is flagged as a scam, its status is strictly `scam` regardless of whether the text claims to be an "offer" or "interview". Fake offers are never added to the user's tracker.

### C. Canonical Multi-Touch Deduplication (`tracker_merge.py`)
Job seekers receive multiple emails per company (e.g., application confirmation on Oct 10, followed by an interview invite on Oct 16).
* Applications are indexed by canonical `(company, role)`.
* Status only advances forward: `applied` &rarr; `interview` &rarr; `offer` (or `rejected`).
* Full email timelines are preserved for complete audit trails.

### D. 7-Day Follow-Up Alarm Engine (`follow_up_logic.py`)
* Compares the latest email date to reference date `today` (configurable in the UI).
* Applications remaining in `applied` status for &ge; 7 days without reply trigger an overdue alarm.
* Dynamically generates polite, ready-to-send follow-up email drafts with customized subject and body.

### E. Interview Prep Copilot (`interview_prep.py` — Stretch Goal)
For any application in the `interview` column, one click generates:
* Company profile and business brief.
* Core technical focus topics (e.g., System Design, Concurrency, React Performance).
* Likely behavioral/technical questions with strategic answer tips.
* Smart, impressive reverse-interview questions to ask the hiring team.

---

## ⚙️ 4. How the Solution Works

### End-to-End Pipeline Workflow
```
[inbox.json] (20 Mocked Emails)
      │
      ▼
(1) Deterministic Pre-Scanner (rule_hints.py)
      │  └── Detects UPI fee, Aadhaar/PAN, Gmail spoofing, Telegram redirects
      ▼
(2) Gemini 2.5 Flash Classifier (gemini_classifier.py)
      │  ├── Structured JSON response schema
      │  ├── Scam Override Rule (fake offers never reach tracker)
      │  └── Rule 06 Disk Cache (gemini_cache.json for offline demo)
      ▼
(3) State Machine & Tracker Merger (tracker_merge.py)
      │  ├── Quarantines scams into Scam Shield
      │  └── Deduplicates multi-touch emails into 4 Kanban columns
      ▼
(4) Follow-Up Reminder Engine (follow_up_logic.py)
      │  ├── Identifies unanswered applications ≥ 7 days
      │  └── Pre-generates personalized follow-up drafts
      ▼
(5) Interactive Glassmorphism UI (static/index.html & static/app.js)
         ├── Overview: Real-time metrics and system pipeline visualization
         ├── Tracker: Interactive 4-column Kanban board with email timelines
         ├── Scam Shield: Red-flag quarantine cards with explicit explanations
         ├── Follow Ups: Due alarms with copyable email draft generator
         └── Help & Sandbox: Full user guide and live email testing console
```

---

## 📋 5. Important Rules Compliance

| Rule Requirement | Status | Implementation Details |
|---|---|---|
| **Repository Size < 10 MB** | ✅ **Passed (0.15 MB)** | Raw Kaggle datasets (>47 MB) are excluded via `.gitignore`. Repository contains only clean code, assets, and mocked data (~150 KB total). |
| **Public GitHub Repository** | ✅ **Passed** | Fully public repository with open-source MIT license. |
| **Single Branch Only** | ✅ **Passed (`main`)** | All commits are unified on a single branch (`main`) with zero secondary branches. |
| **Max 2 Attempts Allowed** | ✅ **Passed** | Delivered in a clean, tested commit. |
| **Rule 05 — Mocked Inbox Disclosure** | ✅ **Passed** | Clearly labeled "Mocked Inbox (Rule 05)" in UI headers, cards, and modal inspector. |
| **Rule 06 — Offline Cache** | ✅ **Passed** | All 20 email responses pre-cached in `gemini_cache.json`. If disconnected, demo runs 100% offline. |
| **Rule 07 — 20-Email Inbox** | ✅ **Passed** | Handcrafted `inbox.json` with 20 realistic emails: 6 applied, 3 interviews, 2 verified offers, 3 rejections, and 5 scam archetypes. |

---

## 🔍 6. Assumptions Made

1. **Mocked Inbox Context:** The 20 emails in `inbox.json` reflect a realistic 3-week timeline for a laid-off engineer applying across startups and tech firms.
2. **Follow-Up Threshold:** 7 days without response is the industry-standard window for professional job follow-ups.
3. **No Fees in Legitimate Hiring:** Legitimate employers never ask candidates to pay for training, equipment, or gate passes during recruitment.
4. **Identity Security:** Requesting government identification (Aadhaar/PAN) or banking cancelled cheques via plain email prior to an interview is treated as identity theft.
5. **State Progression:** Once an application advances to `interview` or `offer`, subsequent acknowledgments do not downgrade its status. `rejected` is terminal.

---

## 🧪 7. Validation & Automated Tests

Run the comprehensive test suite locally to verify pipeline integrity:

```bash
# 1. Run pipeline audit and Kanban verification
python audit.py

# 2. Run live Gemini API integration test (with live key)
python test_live_gemini.py
```

### Test Suite Output Summary (`audit.py`):
```text
=== PIPELINE SUMMARY ===
  Total emails processed : 20
  Scams quarantined      : 5
  Follow-ups due (>=7d)  : 4
  Active applications    : 14
  Interviews             : 3 (all with prep notes)
  Offers                 : 2 (verified genuine)
  Rejections             : 3
  Cache entries verified : >= 20 (Rule 06 compliant)
```

---

## 🛡️ 8. Security & Code Quality

* **Zero Secret Leakage:** `.env` and all credential files are protected by `.gitignore` and never committed.
* **Input Sanitization:** Frontend controller uses strict HTML escaping on all dynamic data to prevent XSS vulnerabilities.
* **Deterministic Fallback:** Robust fallback mechanisms protect against API rate limits or network dropouts during live presentations.
* **Accessibility:** Clean typography using Outfit & Inter, WCAG-compliant color contrast ratios, dash-free intuitive navigation, and responsive layouts across viewports.

---

## 👥 Authors & Acknowledgments
Built for **GDG Garbathon 2026** by Kalpit. Powered by Google Gemini 2.5 Flash and FastAPI.
