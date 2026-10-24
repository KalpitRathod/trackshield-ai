"""
Cybercrime 1930 & National Cyber Crime Reporting Portal (cybercrime.gov.in)
Automated Forensic Evidence Dossier & Official Complaint Generator.
Part of TaalMail AI (GDG Garbathon 2026).
"""
import re
from typing import Dict, Any, List


def extract_evidence(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts cyber forensic evidence from email sender, subject, and body."""
    sender = email_data.get("from", "")
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    full_text = f"{sender}\n{subject}\n{body}"

    # Extract sender domain
    domain_match = re.search(r"@([a-zA-Z0-9.\-_]+)", sender)
    domain = domain_match.group(1).lower().strip(">") if domain_match else "unknown"

    # Extract UPI IDs from email body (e.g. info.batch@upi, tm-onboard@icici)
    upi_id = None
    upi_explicit = re.search(r"(?:upi(?:\s+id)?(?:\s+to)?\s*:?\s*)([a-zA-Z0-9.\-_]+@[a-zA-Z0-9]+)", body, re.IGNORECASE)
    if upi_explicit and not upi_explicit.group(1).lower().endswith((".com", ".org", ".net", ".io", ".co")):
        upi_id = upi_explicit.group(1).lower()
    else:
        vpa_match = re.search(r"\b([a-zA-Z0-9.\-_]+@(upi|icici|paytm|okaxis|okhdfcbank|sbi|ybl|axl|apl|barodampay|postbank))\b", body, re.IGNORECASE)
        if vpa_match:
            upi_id = vpa_match.group(1).lower()

    # Extract demanded fee/deposit (avoid matching LPA salary)
    amount_match = re.search(r"(?:fee|deposit|charge|pay|transfer)\s*(?:of|towards)?\s*(?:Rs\.?|INR|₹)\s*([\d,]+)", body, re.IGNORECASE)
    if not amount_match:
        amount_match = re.search(r"(?:Rs\.?|INR|₹)\s*([\d,]+)(?!\s*lpa|\s*lakh)", body, re.IGNORECASE)
    demanded_amount = f"Rs {amount_match.group(1)}" if amount_match else None

    # Extract sensitive document requests
    docs_demanded = []
    if re.search(r"\baadhaar\b", full_text, re.IGNORECASE):
        docs_demanded.append("Aadhaar Card (Photos/Scans)")
    if re.search(r"\bpan(\s*card)?\b", full_text, re.IGNORECASE):
        docs_demanded.append("PAN Card")
    if re.search(r"\b(cancelled cheque|cheque)\b", full_text, re.IGNORECASE):
        docs_demanded.append("Cancelled Bank Cheque")
    if re.search(r"\bbank(ing)? (password|details|account)\b", full_text, re.IGNORECASE):
        docs_demanded.append("Banking Credentials")

    # Extract off-platform handle (Telegram)
    tg_match = re.search(r"(@[a-zA-Z0-9_]{5,})", full_text)
    telegram_handle = tg_match.group(1) if tg_match else None

    # Determine fraud category
    if upi_id or demanded_amount:
        category = "Online Financial Fraud • Job Recruitment Advance Fee Scam"
        act_sections = "Section 66D IT Act (Cheating by Personation) & Section 318 BNS / 420 IPC"
    elif docs_demanded:
        category = "Identity Theft & Document Harvesting Fraud"
        act_sections = "Section 66C IT Act (Identity Theft) & Section 419 IPC"
    elif telegram_handle:
        category = "Phishing & Malicious Off-Platform Extortion Funnel"
        act_sections = "Section 66D IT Act (Cheating by Computer Resource)"
    else:
        category = "Corporate Impersonation & Malicious Phishing"
        act_sections = "Section 66D IT Act"

    return {
        "sender": sender,
        "sender_domain": domain,
        "upi_id": upi_id,
        "demanded_amount": demanded_amount,
        "docs_demanded": docs_demanded,
        "telegram_handle": telegram_handle,
        "category": category,
        "act_sections": act_sections,
    }


def generate_complaint_dossier(email_data: Dict[str, Any], scam_reasons: List[str] = None) -> Dict[str, Any]:
    """
    Generates a ready-to-file complaint dossier for:
    1. National Cyber Crime Reporting Portal (cybercrime.gov.in)
    2. National Cyber Crime Helpline (1930)
    """
    evidence = extract_evidence(email_data)
    date_str = email_data.get("date", "2026-10-24")
    company = email_data.get("company") or email_data.get("subject", "").split(":")[0]
    role = email_data.get("role", "Candidate")
    reasons = scam_reasons or email_data.get("scam_reasons", [])

    # Format official complaint body
    bullets_reasons = "\n".join([f"• {r}" for r in reasons]) if reasons else "• High-risk fraudulent recruitment indicators."
    docs_str = ", ".join(evidence["docs_demanded"]) if evidence["docs_demanded"] else "None explicitly harvested"
    amount_str = evidence["demanded_amount"] or "No direct fee (Identity theft / diversion scam)"
    upi_str = evidence["upi_id"] or "None detected"
    tg_str = evidence["telegram_handle"] or "None"

    complaint_text = f"""OFFICIAL COMPLAINT DOSSIER FOR CYBERCRIME.GOV.IN / HELPLINE 1930
Reference Law: {evidence['act_sections']}
Category: {evidence['category']}
Date of Incident: {date_str}

1. SUSPECT PARTICULARS:
• Sender Email: {evidence['sender']}
• Suspect Domain: {evidence['sender_domain']}
• Impersonated Entity: {company}
• Beneficiary UPI / Account ID: {upi_str}
• Unofficial Chat Handle: {tg_str}

2. FINANCIAL & IDENTITY EXTORTION DETAILS:
• Upfront Fee Demanded: {amount_str}
• Target Documents Harvested: {docs_str}

3. INCIDENT SUMMARY:
I received an unsolicited communication purporting to be an official employment offer/invitation from {company} for the role of {role}. Upon technical verification, the sender was identified as an unauthorized imposter attempting deliberate fraud.

Detected Fraud Indicators:
{bullets_reasons}

4. RELIEF & INVESTIGATION REQUESTED:
1. Register this cybercrime under Section 66D IT Act and relevant provisions of BNS/IPC.
2. Direct NPCI and beneficiary banks to immediately freeze the fraudulent UPI handle ({upi_str}) to prevent further victim losses.
3. Coordinate with domain registrars to suspend the lookalike domain ({evidence['sender_domain']}).
4. Record sender identity for cyber-forensic blacklist tracking.

Submitted via TaalMail AI Automated Defense Suite."""

    recommended_actions = [
        "Call 1930 immediately to report the suspect UPI handle to the National Cyber Financial Citizen Fraud Registry (CFCFR).",
        "Never transfer any fee; legitimate corporate recruiters in India strictly do not charge training or badge fees.",
        "If you previously shared Aadhaar copies, use the UIDAI mAadhaar app to lock your Biometrics and Aadhaar number.",
        "Report the sender domain at registry spam abuse desks and cybercrime.gov.in."
    ]

    return {
        "status": "ready",
        "portal_url": "https://cybercrime.gov.in",
        "helpline": "1930",
        "evidence": evidence,
        "complaint_text": complaint_text.strip(),
        "recommended_actions": recommended_actions
    }
