import json

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def handler(request):
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    if request.method != 'GET':
        return {
            'statusCode': 405,
            'headers': CORS_HEADERS,
            'body': json.dumps({'success': False, 'error': 'Method not allowed'})
        }

    return {
        'statusCode': 200,
        'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'healthy', 'message': 'Resume Analyzer API is running'})
    }
