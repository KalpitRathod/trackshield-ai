import urllib.request, json, urllib.error

import os
API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Skip already-confirmed failures, test promising ones
candidates = [
    'gemini-flash-lite-latest',
    'gemini-pro-latest',
    'gemini-flash-latest',
    'gemini-3.8-flash',
    'gemini-3.7-flash',
    'gemini-3.6-flash',
    'gemini-3.5-flash',
    'gemini-3.1-flash-lite',
    'gemini-3-flash-preview',
    'gemma-4-26b-a4b-it',
]

print('Testing JSON-mode support on each candidate model...\n')
for model_id in candidates:
    test_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={API_KEY}'
    payload = {
        'contents': [{'parts': [{'text': 'Return this JSON exactly: {"status": "working"}'}]}],
        'generationConfig': {
            'temperature': 0,
            'maxOutputTokens': 50,
            'responseMimeType': 'application/json'
        }
    }
    req = urllib.request.Request(
        test_url,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req, timeout=12)
        result = json.loads(resp.read())
        text = result['candidates'][0]['content']['parts'][0]['text']
        parsed = json.loads(text)
        print(f'  WORKS (JSON mode) -> {model_id}: {parsed}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        # Try without JSON mode if it was a 400
        if e.code == 400 and 'responseMimeType' in body:
            payload2 = {
                'contents': [{'parts': [{'text': 'Return this JSON exactly: {"status": "working"}'}]}],
                'generationConfig': {'temperature': 0, 'maxOutputTokens': 50}
            }
            req2 = urllib.request.Request(test_url, data=json.dumps(payload2).encode(), headers={'Content-Type': 'application/json'}, method='POST')
            try:
                resp2 = urllib.request.urlopen(req2, timeout=12)
                result2 = json.loads(resp2.read())
                text2 = result2['candidates'][0]['content']['parts'][0]['text']
                print(f'  WORKS (text mode) -> {model_id}: {text2.strip()[:40]}')
            except Exception as e2:
                print(f'  FAIL both modes -> {model_id}')
        else:
            print(f'  FAIL {e.code} -> {model_id}: {body[:80]}')
    except Exception as e:
        print(f'  ERR -> {model_id}: {str(e)[:60]}')
