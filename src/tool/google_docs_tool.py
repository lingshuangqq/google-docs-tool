import re
from googleapiclient.errors import HttpError

# --- Internal Helper Functions ---

def _execute_batch_update(docs_service, document_id: str, requests: list) -> dict:
    """Executes a batchUpdate request and handles common errors."""
    try:
        if not requests:
            return {"status": "success", "message": "No changes were needed."}
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        return {"status": "success", "message": f"Successfully updated document {document_id}."}
    except HttpError as err:
        error_message = f"An HttpError occurred: {err.reason}"
        return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Markdown Parsing and Request Generation ---

def _get_markdown_requests(markdown_text: str, start_index: int):
    """Converts a markdown string into a list of Google Docs API requests."""
    all_requests = []
    current_index = start_index
    lines = markdown_text.split('\n')

    for line in lines:
        line_start_index = current_index
        text_to_process = line
        paragraph_style = None

        # 1. Handle Paragraph Style (Headers)
        if line.startswith('# '):
            text_to_process = line[2:]
            paragraph_style = {'namedStyleType': 'HEADING_1'}
        elif line.startswith('## '):
            text_to_process = line[3:]
            paragraph_style = {'namedStyleType': 'HEADING_2'}
        elif line.startswith('### '):
            text_to_process = line[4:]
            paragraph_style = {'namedStyleType': 'HEADING_3'}

        # 2. Handle Inline Styles (Bold)
        matches = list(re.finditer(r'\*\*(.*?)\*\*', text_to_process))
        last_end = 0
        
        if not matches:
            if text_to_process:
                all_requests.append({'insertText': {'location': {'index': current_index}, 'text': text_to_process}})
                all_requests.append({'updateTextStyle': {'range': {'startIndex': current_index, 'endIndex': current_index + len(text_to_process)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})
                current_index += len(text_to_process)
        else:
            for match in matches:
                start, end = match.span()
                plain_text_before = text_to_process[last_end:start]
                if plain_text_before:
                    all_requests.append({'insertText': {'location': {'index': current_index}, 'text': plain_text_before}})
                    all_requests.append({'updateTextStyle': {'range': {'startIndex': current_index, 'endIndex': current_index + len(plain_text_before)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})
                    current_index += len(plain_text_before)
                
                bold_text = match.group(1)
                if bold_text:
                    all_requests.append({'insertText': {'location': {'index': current_index}, 'text': bold_text}})
                    all_requests.append({'updateTextStyle': {'range': {'startIndex': current_index, 'endIndex': current_index + len(bold_text)}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
                    current_index += len(bold_text)
                last_end = end

            plain_text_after = text_to_process[last_end:]
            if plain_text_after:
                all_requests.append({'insertText': {'location': {'index': current_index}, 'text': plain_text_after}})
                all_requests.append({'updateTextStyle': {'range': {'startIndex': current_index, 'endIndex': current_index + len(plain_text_after)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})
                current_index += len(plain_text_after)

        all_requests.append({'insertText': {'location': {'index': current_index}, 'text': '\n'}})
        if paragraph_style:
            all_requests.append({'updateParagraphStyle': {'range': {'startIndex': line_start_index, 'endIndex': current_index}, 'paragraphStyle': paragraph_style, 'fields': 'namedStyleType'}})
        current_index += 1

    return all_requests

# --- Main Public Functions ---

def replace_markdown_placeholders(docs_service, document_id: str, replacements: dict):
    """Finds and replaces multiple placeholders with formatted markdown content."""
    try:
        doc = docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
        content = doc.get('body', {}).get('content', [])
        
        found_holders = []
        for element in content:
            if 'paragraph' in element:
                for run in element['paragraph']['elements']:
                    if 'textRun' in run and run['textRun']['content']:
                        segment_text = run['textRun']['content']
                        for key in replacements.keys():
                            for match in re.finditer(re.escape(key), segment_text):
                                start = run['startIndex'] + match.start()
                                end = run['startIndex'] + match.end()
                                found_holders.append({'key': key, 'range': {'startIndex': start, 'endIndex': end}})

        found_holders.sort(key=lambda x: x['range']['startIndex'], reverse=True)
        
        if not found_holders:
            return {"status": "error", "message": "Could not find any of the specified placeholders."}

        all_requests = []
        for holder in found_holders:
            key = holder['key']
            markdown_content = replacements[key]
            start_index = holder['range']['startIndex']

            all_requests.append({'deleteContentRange': {'range': holder['range']}})
            
            # Get the list of requests for the markdown content
            markdown_requests = _get_markdown_requests(markdown_content, start_index)
            all_requests.extend(markdown_requests)
            
        return _execute_batch_update(docs_service, document_id, all_requests)

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

def create_doc(drive_service, title: str, folder_id: str = None):
    """Creates a new Google Doc."""
    file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    try:
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        return {"status": "success", "document_id": file.get('id')}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred creating the document: {e}"}

def clear_google_doc(docs_service, document_id: str) -> dict:
    """Deletes all content from a Google Doc."""
    try:
        doc = docs_service.documents().get(documentId=document_id).execute()
        body_content = doc.get('body', {}).get('content', [])
        if len(body_content) > 1:
            end_index = body_content[-1].get('endIndex', 1)
            if end_index > 2:
                requests = [{'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}}]
                return _execute_batch_update(docs_service, document_id, requests)
        return {"status": "success", "message": "Document is already empty."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}
