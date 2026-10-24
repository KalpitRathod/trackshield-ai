import urllib.request, json, sys

# Test 1: Pipeline API
resp = urllib.request.urlopen('http://127.0.0.1:8000/api/pipeline?today=2026-10-24')
data = json.loads(resp.read())

print('=== PIPELINE SUMMARY ===')
s = data['summary']
print(f"  Total emails processed : {s['total_emails_analyzed']}")
print(f"  Scams quarantined      : {s['scams_blocked']}")
print(f"  Follow-ups due (>=7d)  : {s['follow_ups_due']}")
print(f"  Active applications    : {s['active_applications']}")
print(f"  Interviews             : {s['interview_count']}")
print(f"  Offers                 : {s['offer_count']}")
print(f"  Rejections             : {s['rejected_count']}")
print(f"  Cache hits             : {s['cached_responses']}")
print(f"  Live Gemini calls      : {s['live_responses']}")

print()
print('=== KANBAN COLUMNS ===')
for col, items in data['columns'].items():
    print(f'\n  {col.upper()} ({len(items)} cards):')
    for a in items:
        fu    = ' *** FOLLOWUP_DUE ***' if a.get('follow_up_due') else ''
        prep  = ' [PREP_READY]' if a.get('interview_prep') else ''
        ct    = a.get('email_count', 1)
        mrgd  = f' [MERGED x{ct}]' if ct > 1 else ''
        idate = a.get('interview_date') or '-'
        days  = a.get('days_since_last_email', 0)
        print(f'    {a["company"]:20s} | {a["role"][:28]:28s} | last={a["last_email_date"]} | days={days:2d}{fu}{prep}{mrgd} | idate={idate}')

print()
print('=== SCAM QUARANTINE CARDS ===')
for s in data['scams']:
    print(f'\n  [{s["company"]}] via <{s["from"]}>')
    for r in s['scam_reasons']:
        print(f'    ! {r}')

print()
print('=== FOLLOW-UP DRAFT VERIFICATION ===')
for a in data['applications']:
    if a.get('follow_up_due'):
        d = a.get('follow_up_draft')
        if d:
            print(f'  {a["company"]} -> Draft subject: "{d["subject"][:60]}"  DRAFT_HAS_BODY={bool(d["body"])}')
        else:
            print(f'  {a["company"]} -> MISSING DRAFT (BUG)')

print()
print('=== INTERVIEW PREP VERIFICATION ===')
for a in data['applications']:
    if a.get('status') == 'interview':
        prep = a.get('interview_prep')
        if prep:
            q_count = len(prep.get('key_questions', []))
            sq_count = len(prep.get('smart_questions_to_ask', []))
            fp_count = len(prep.get('tech_focus', []))
            print(f'  {a["company"]} | {a["role"]} -> focus={fp_count} topics, {q_count} Qs, {sq_count} smart-Qs')
        else:
            print(f'  {a["company"]} -> NO PREP NOTES (BUG)')

print()
print('=== CACHE / OFFLINE DEMO (RULE 06) ===')
import os
cache_file = r'c:\Users\Kalpit\Desktop\Code\GDG Garbathon\gemini_cache.json'
cache = json.load(open(cache_file))
print(f'  Cache entries: {len(cache)} (>= 20)')
print(f'  All inbox emails classified offline: {len(cache) >= 20}')
