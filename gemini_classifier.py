"""
Gemini Structured Email Classifier with Prompt-Engineered Scam Detection & File-Based Caching.
Adheres to Hackathon Rules:
- Rule 06: Response caching to gemini_cache.json for guaranteed offline demo.
- Structured JSON output schema.
- Scam overrides all other statuses.
"""
import os
import json
import urllib.request
import urllib.error

# Auto-load .env file if present (no external dependencies needed)
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())

_load_dotenv()
from typing import Dict, Any, Optional
from rule_hints import get_rule_hints


CACHE_FILE = os.path.join(os.path.dirname(__file__), "gemini_cache.json")

SYSTEM_INSTRUCTION = """You are an expert AI Career Copilot and Scam Shield for job seekers.
Your task is to analyze candidate emails and accurately classify them into an employment pipeline.

CRITICAL RULES:
1. SCAM OVERRIDES EVERYTHING ELSE. If an email exhibits ANY red flag of being fraudulent, phishing, or a recruitment scam, status MUST be "scam" (even if the email claims to be an offer, interview, or appointment letter).
2. Pay close attention to the SENDER DOMAIN. A mismatch between the claimed corporate brand (e.g. Infosys, TCS, Google) and a free-mail provider (@gmail.com, @yahoo.com) or a lookalike domain (e.g. infosys-careers.co, tcs-careers-portal.com) is definitive proof of a scam.
3. Recognize genuine offers: A genuine offer letter from an official company domain with standard onboarding procedures, no fee requests, and formal contracts should be classified as "offer" with zero scam reasons. Do not cry wolf on legitimate opportunities.
4. If status is "interview", extract the interview date in YYYY-MM-DD format if mentioned, otherwise null.

RED FLAG SCAM RULES:
- Rule 1 (Upfront Fee / Deposit): Demanding any training fee, registration charge, laptop security deposit, gate pass fee, or refundable deposit via UPI/IMPS/GPay. Legitimate employers NEVER charge candidates.
- Rule 2 (Identity & KYC Pre-Offer): Immediate demand for Aadhaar card, PAN card, banking details, or cancelled cheque via email reply before any contract or interview.
- Rule 3 (Free-Mail Impersonation): Reputable enterprise companies emailing from @gmail.com, @yahoo.com, @outlook.com, etc.
- Rule 4 (Lookalike / Typosquat Domain): Sender domain mimicking brands using hyphens or generic TLDs (e.g., techmahindra-careers.co vs techmahindra.com).
- Rule 5 (Off-Platform Chat): Moving interviews or candidate screening to Telegram, WhatsApp, or private chat channels.
- Rule 6 (Unsolicited Direct Selection): High salary or guaranteed offer without any assessment, technical screening, or interview.
- Rule 7 (High Urgency Pressure): Artificial deadlines ("pay within 2 hours or forfeit") to rush the applicant.

OUTPUT SCHEMA (Must be pure JSON without markdown backticks):
{
  "company": "string",
  "role": "string",
  "status": "applied | interview | rejected | offer | scam",
  "scam_reasons": ["string"],
  "confidence": 0.95,
  "interview_date": "YYYY-MM-DD or null"
}
"""

FEW_SHOT_EXAMPLES = [
    {
        "input": "From: hr.infosys.jobs@gmail.com | Subject: Selection letter - pay Rs 4,999 training fee | Body: You are selected as Systems Associate. Pay refundable fee and send Aadhaar and PAN.",
        "output": {
            "company": "Infosys",
            "role": "Systems Associate",
            "status": "scam",
            "scam_reasons": [
                "Domain spoofing: Free-mail @gmail.com impersonating Infosys",
                "Demands upfront refundable training fee of Rs 4,999",
                "Harvests sensitive Aadhaar and PAN documents upfront"
            ],
            "confidence": 0.99,
            "interview_date": None
        }
    },
    {
        "input": "From: careers@zentech.in | Subject: Application received: Backend Engineer | Body: Thanks for applying for Backend Engineer. Our team will review your qualifications and reach out.",
        "output": {
            "company": "Zentech",
            "role": "Backend Engineer",
            "status": "applied",
            "scam_reasons": [],
            "confidence": 0.98,
            "interview_date": None
        }
    },
    {
        "input": "From: talent@finly.co | Subject: Interview invite: Round 1 on 27 Oct | Body: Please join Google Meet on 2026-10-27 at 3:00 PM for Frontend Engineer round 1.",
        "output": {
            "company": "Finly",
            "role": "Frontend Engineer",
            "status": "interview",
            "scam_reasons": [],
            "confidence": 0.97,
            "interview_date": "2026-10-27"
        }
    },
    {
        "input": "From: recruiting@stripe.com | Subject: Offer of Employment: Staff Infrastructure Engineer | Body: On behalf of Stripe, we extend a formal offer. Review terms on official portal stripe.com/careers/portal.",
        "output": {
            "company": "Stripe",
            "role": "Staff Infrastructure Engineer",
            "status": "offer",
            "scam_reasons": [],
            "confidence": 0.99,
            "interview_date": None
        }
    }
]


def load_cache() -> Dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache_data: Dict[str, Any]) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save cache: {e}")


# Confirmed working models (JSON mode tested 2026-10-24):
# Primary: gemini-flash-lite-latest   ✅ JSON mode OK
# Fallback: gemini-3.1-flash-lite     ✅ JSON mode OK
GEMINI_MODELS = ["gemini-flash-lite-latest", "gemini-3.1-flash-lite"]


def call_gemini_api(prompt_text: str, api_key: str, model: str = "gemini-flash-lite-latest") -> Dict[str, Any]:
    """Call official Gemini REST API directly. Auto-retries on next model if 404/429."""
    models_to_try = [model] + [m for m in GEMINI_MODELS if m != model]

    last_err = None
    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                result_json = json.loads(resp.read().decode("utf-8"))
                candidates = result_json.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    text = candidates[0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)
                    parsed["_model_used"] = m
                    return parsed
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (404, 503):
                continue   # try next model
            raise
        except Exception as e:
            last_err = e
            continue
    raise ValueError(f"All models failed. Last error: {last_err}")


def classify_email(email_data: Dict[str, Any], api_key: Optional[str] = None, force_live: bool = False) -> Dict[str, Any]:
    """
    Classify a single email into the pipeline schema.
    Rule 06: Uses gemini_cache.json if present unless force_live=True with a valid key.
    """
    email_id = str(email_data.get("id", ""))
    cache = load_cache()
    
    # 1. Check local cache (Rule 06: Instant offline demo support)
    if not force_live and email_id in cache:
        cached_result = dict(cache[email_id])
        cached_result["_from_cache"] = True
        return cached_result
        
    # 2. Extract cheap rule hints
    hints = get_rule_hints(email_data)
    
    # Check for API key
    active_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if active_key and force_live:
        prompt = f"""{SYSTEM_INSTRUCTION}

FEW-SHOT EXAMPLES:
{json.dumps(FEW_SHOT_EXAMPLES, indent=2)}

INPUT EMAIL TO CLASSIFY:
Sender: {email_data.get('from', '')}
Sender Domain: {hints.get('sender_domain', '')}
Free-mail Domain: {hints.get('is_freemail', False)}
Deterministic Rule Hints: {hints.get('hints', [])}
Date: {email_data.get('date', '')}
Subject: {email_data.get('subject', '')}
Body:
{email_data.get('body', '')}

Return ONLY the raw JSON object adhering to the schema:
"""
        try:
            gemini_result = call_gemini_api(prompt, active_key)
            # Update cache
            cache[email_id] = gemini_result
            save_cache(cache)
            gemini_result["_from_cache"] = False
            return gemini_result
        except Exception as err:
            print(f"Gemini API call failed ({err}), falling back to cache or heuristics.")

    # 3. Fallback: If in cache, return cached
    if email_id in cache:
        cached_result = dict(cache[email_id])
        cached_result["_from_cache"] = True
        return cached_result

    # 4. Ultimate fallback using rule hints heuristics
    # Try to infer company from sender domain (e.g. careers@zentech.in -> Zentech)
    sender_domain = hints.get("sender_domain", "")
    domain_root = sender_domain.split(".")[0] if sender_domain else ""
    guessed_company = domain_root.replace("-", " ").title() if domain_root else "Unknown Employer"

    if hints.get("has_scam_signals"):
        return {
            "company": guessed_company,
            "role": email_data.get("subject", "Opportunity"),
            "status": "scam",
            "scam_reasons": hints.get("hints", ["High-risk hiring scam detected"]),
            "confidence": 0.90,
            "interview_date": None,
            "_from_cache": False
        }
    
    return {
        "company": guessed_company,
        "role": email_data.get("subject", "Role"),
        "status": "applied",
        "scam_reasons": [],
        "confidence": 0.85,
        "interview_date": None,
        "_from_cache": False
    }
