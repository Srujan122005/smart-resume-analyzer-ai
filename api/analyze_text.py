import json
from backend.app import analyze_match

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def parse_request_payload(request):
    if hasattr(request, 'json'):
        try:
            return request.json
        except Exception:
            pass

    body = getattr(request, 'body', None)
    if isinstance(body, (bytes, bytearray)):
        body = body.decode('utf-8', errors='ignore')

    if not body:
        return {}

    try:
        return json.loads(body)
    except Exception:
        return {}


def handler(request):
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': CORS_HEADERS,
            'body': json.dumps({'success': False, 'error': 'Method not allowed'})
        }

    payload = parse_request_payload(request)
    resume_text = (payload.get('resume_text') or '').strip()
    job_description = (payload.get('job_description') or '').strip()

    if not resume_text:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'success': False, 'error': 'Resume text is required'})
        }

    if not job_description:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'success': False, 'error': 'Job description is required'})
        }

    result = analyze_match(resume_text, job_description)

    return {
        'statusCode': 200,
        'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
        'body': json.dumps({'success': True, 'data': result, 'message': 'Analysis completed successfully'})
    }
