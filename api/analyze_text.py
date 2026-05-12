import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.app import analyze_match

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def handler(request):
    """Vercel serverless handler for /analyze-text endpoint."""
    try:
        if request.method == 'OPTIONS':
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': 'Method not allowed'})
            }

        # Parse JSON body
        body = {}
        try:
            if hasattr(request, 'json') and callable(request.json):
                body = request.json()
            elif hasattr(request, 'body'):
                raw_body = request.body
                if isinstance(raw_body, bytes):
                    raw_body = raw_body.decode('utf-8')
                body = json.loads(raw_body) if raw_body else {}
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': f'Invalid request body: {str(e)}'})
            }

        resume_text = (body.get('resume_text') or '').strip()
        job_description = (body.get('job_description') or '').strip()

        if not resume_text:
            return {
                'statusCode': 400,
                'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': 'Resume text is required'})
            }

        if not job_description:
            return {
                'statusCode': 400,
                'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': 'Job description is required'})
            }

        result = analyze_match(resume_text, job_description)

        return {
            'statusCode': 200,
            'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
            'body': json.dumps({'success': True, 'data': result, 'message': 'Analysis completed successfully'})
        }
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': f'Server error: {str(e)}'})
        }
