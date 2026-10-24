"""
Rule Hints Engine for Job Search & Scam Detection Pipeline.
Lightweight, deterministic heuristics that extract sender domain, detect high-risk signals,
and pass hints into the Gemini classifier (as well as acting as offline fallback).
"""
import re
from typing import Dict, List, Any


FREE_MAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "yandex.com", "proton.me", "protonmail.com"
}

KNOWN_ENTERPRISES = [
    "infosys", "tcs", "tata consultancy", "wipro", "cognizant",
    "tech mahindra", "hcl", "accenture", "google", "microsoft",
    "amazon", "meta", "stripe", "uber", "swiggy", "zomato",
    "flipkart", "razorpay", "cred", "zerodha", "phonepe", "postman"
]

SCAM_KEYWORDS = [
    (r"\b(training fee|registration fee|processing fee|security deposit|gate pass|laptop fee|refundable fee)\b", "Demands upfront payment/fee"),
    (r"\b(aadhaar|pan card|cancelled cheque|bank account details|banking password|otp)\b", "Harvests sensitive identity documents (Aadhaar/PAN/Cheque)"),
    (r"\b(telegram|whatsapp|signal)\b", "Directs interview communication to unofficial chat app (Telegram/WhatsApp)"),
    (r"\b(without (any )?(test|exam|interview)|no prior interview|direct joining|guaranteed selection)\b", "Unsolicited selection without legitimate interview process"),
    (r"\b(pay rs\.?|deposit rs\.?|transfer rs\.?|upi id|gpay|phonepe)\b", "Requests immediate money transfer via UPI/IMPS"),
    (r"\b(urgent|within 24 hours|today before \d|cancel your appointment if not paid)\b", "High-pressure urgency tactics to enforce hasty action")
]

LOOKALIKE_PATTERNS = [
    r"-careers\.",
    r"-jobs\.",
    r"-hiring\.",
    r"-portal\.",
    r"-onboard\."
]


def extract_domain(sender_email: str) -> str:
    """Extract domain from sender email address."""
    match = re.search(r"@([a-zA-Z0-9.\-_]+)", sender_email)
    if match:
        return match.group(1).lower().strip(">")
    return ""


def get_rule_hints(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes email sender, subject, and body for red flags.
    Returns structured hints for Gemini prompt and fallback logic.
    """
    sender = email_data.get("from", "")
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    combined_text = f"{subject}\n{body}".lower()
    
    sender_domain = extract_domain(sender)
    is_freemail = sender_domain in FREE_MAIL_DOMAINS
    
    flags: List[str] = []
    
    # 1. Check for free-mail claiming enterprise
    for ent in KNOWN_ENTERPRISES:
        if ent in combined_text or ent in sender.lower():
            if is_freemail:
                flags.append(f"Domain spoofing: Free-mail provider (@{sender_domain}) claiming corporate identity '{ent.title()}'")
                break
    
    # 2. Check for lookalike / typosquatting domain
    for pattern in LOOKALIKE_PATTERNS:
        if re.search(pattern, sender_domain):
            flags.append(f"Suspicious domain structure: Lookalike recruiting domain pattern detected ({sender_domain})")
            break
            
    # 3. Check for scam keywords
    for pattern, description in SCAM_KEYWORDS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            if description not in flags:
                flags.append(description)
                
    has_scam_signals = len(flags) > 0
    suggested_status = "scam" if has_scam_signals else None
    
    return {
        "sender_domain": sender_domain,
        "is_freemail": is_freemail,
        "has_scam_signals": has_scam_signals,
        "hints": flags
    }


if __name__ == "__main__":
    test_email = {
        "from": "hr.infosys.jobs@gmail.com",
        "subject": "Offer letter - pay Rs 4,999 training fee",
        "body": "You are selected. Pay the refundable fee and send Aadhaar and PAN..."
    }
    print(get_rule_hints(test_email))
