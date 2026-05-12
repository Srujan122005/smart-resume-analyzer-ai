import base64
import json
import os
import sys
import tempfile
from email.parser import BytesParser
from email.policy import default
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.app import allowed_file, extract_text_from_pdf, analyze_match

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def parse_json_payload(request):
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


def parse_multipart_body(request):
    content_type = request.headers.get('content-type', '') or request.headers.get('Content-Type', '')
    body = getattr(request, 'body', b'')
    if isinstance(body, str):
        body = body.encode('utf-8')

    if not body or 'multipart/form-data' not in content_type:
        return None

    raw = b'Content-Type: ' + content_type.encode('utf-8') + b'\\r\\nMIME-Version: 1.0\\r\\n\\r\\n' + body
    message = BytesParser(policy=default).parsebytes(raw)

    parsed = {'job_description': '', 'resume_file': None}

    for part in message.iter_parts():
        disposition = part.get_content_disposition()
        if disposition != 'form-data':
            continue
        name = part.get_param('name', header='content-disposition')
        if name == 'job_description':
            parsed['job_description'] = part.get_content().strip()
        elif name == 'resume_file':
            filename = part.get_filename()
            content = part.get_payload(decode=True)
            if filename and content is not None:
                parsed['resume_file'] = {'filename': filename, 'content': content}

    return parsed


def build_response(payload, status=200):
    return {
        'statusCode': status,
        'headers': {**CORS_HEADERS, 'Content-Type': 'application/json'},
        'body': json.dumps(payload)
    }


def handler(request):
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    if request.method != 'POST':
        return build_response({'success': False, 'error': 'Method not allowed'}, status=405)

    form = parse_multipart_body(request)
    resume_text = ''
    job_description = ''

    if form and form.get('resume_file'):
        file_item = form['resume_file']
        job_description = (form.get('job_description') or '').strip()
        if not file_item or not file_item.get('filename'):
            return build_response({'success': False, 'error': 'No file selected'}, status=400)

        filename = file_item['filename']
        if not allowed_file(filename):
            return build_response({'success': False, 'error': 'Please upload PDF files only'}, status=400)

        try:
            temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(filename))
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(file_item['content'])
            resume_text = extract_text_from_pdf(temp_path)
        except Exception as err:
            return build_response({'success': False, 'error': f'Error reading uploaded file: {str(err)}'}, status=400)
    else:
        payload = parse_json_payload(request)
        file_name = payload.get('file_name', '')
        file_data = payload.get('file_data', '')
        job_description = (payload.get('job_description') or '').strip()

        if file_name and file_data:
            try:
                decoded_bytes = base64.b64decode(file_data)
                temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(file_name))
                with open(temp_path, 'wb') as temp_file:
                    temp_file.write(decoded_bytes)
                resume_text = extract_text_from_pdf(temp_path)
            except Exception as err:
                return build_response({'success': False, 'error': f'Error reading uploaded file: {str(err)}'}, status=400)

    if not resume_text:
        return build_response({'success': False, 'error': 'Resume text is required'}, status=400)

    if not job_description:
        return build_response({'success': False, 'error': 'Job description is required'}, status=400)

    result = analyze_match(resume_text, job_description)
    return build_response({'success': True, 'data': result, 'message': 'File analyzed successfully'})
