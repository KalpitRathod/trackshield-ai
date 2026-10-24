"""
Live end-to-end test: calls Gemini API with force_live=True
to classify a brand-new email that is NOT in the cache.
"""
import sys
sys.path.insert(0, '.')
from gemini_classifier import classify_email
import os, json

print('=== LIVE GEMINI API TEST ===')
print(f'API key loaded: {bool(os.environ.get("GEMINI_API_KEY"))}')
print()

# Delete email 777 from cache if it exists (to force live call)
cache_path = 'gemini_cache.json'
cache = json.load(open(cache_path))
cache.pop('777', None)
with open(cache_path, 'w') as f:
    json.dump(cache, f, indent=2)
print('Cleared test email from cache -> forcing LIVE Gemini call')
print()

# Test 1: Scam email (should be caught live)
scam_email = {
    'id': 777,
    'date': '2026-10-24',
    'from': 'hr.wipro.onboarding@gmail.com',
    'subject': 'Wipro Job Offer - Pay Rs 3999 Training Fee',
    'body': (
        'Dear Candidate, Congratulations! You have been selected for the role of '
        'Software Engineer at Wipro Ltd without any exam. To process your joining kit, '
        'please transfer Rs 3,999 refundable training fee via UPI to wipro-hr@paytm and '
        'WhatsApp your Aadhaar card and PAN card to +91-99999-00000.'
    )
}

print('Test 1: Scam email (Wipro fee + gmail + Aadhaar)')
result = classify_email(scam_email, force_live=True)
print(f'  Status    : {result["status"]}  (expected: scam)')
print(f'  Company   : {result["company"]}')
print(f'  Confidence: {result["confidence"]}')
print(f'  Model used: {result.get("_model_used", "cache/heuristic")}')
print(f'  From cache: {result.get("_from_cache")}')
print(f'  Reasons:')
for r in result.get('scam_reasons', []):
    print(f'    - {r}')

print()

# Test 2: Genuine interview email
legit_email = {
    'id': 778,
    'date': '2026-10-24',
    'from': 'recruiting@meesho.com',
    'subject': 'Interview Scheduled: Backend Engineer at Meesho - Nov 3, 11AM',
    'body': (
        'Hi Alex, We are pleased to invite you for Round 2 Technical Interview for the '
        'Backend Engineer position at Meesho. Your interview is scheduled for November 3rd '
        '2026 at 11:00 AM IST on Google Meet. Please confirm your availability. '
        'Regards, Meesho Talent Team'
    )
}

# Remove from cache too
cache = json.load(open(cache_path))
cache.pop('778', None)
with open(cache_path, 'w') as f:
    json.dump(cache, f, indent=2)

print('Test 2: Genuine interview invite (Meesho)')
result2 = classify_email(legit_email, force_live=True)
print(f'  Status         : {result2["status"]}  (expected: interview)')
print(f'  Company        : {result2["company"]}')
print(f'  Interview date : {result2["interview_date"]}  (expected: 2026-11-03)')
print(f'  Confidence     : {result2["confidence"]}')
print(f'  Model used     : {result2.get("_model_used", "cache/heuristic")}')
print(f'  Scam reasons   : {result2.get("scam_reasons", [])}  (expected: [])')

print()
print('=== DONE ===')
