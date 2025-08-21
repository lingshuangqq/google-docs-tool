import json
import sys
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Constants ---
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

# --- Internal Helper Functions ---

def _get_docs_service(credentials_file_path: str):
    """Initializes and returns the Google Docs service client from a file path."""
    creds = Credentials.from_service_account_file(credentials_file_path, scopes=SCOPES)
    return build("docs", "v1", credentials=creds)

def _execute_batch_update(service, document_id: str, requests: list) -> dict:
    """Executes a batchUpdate request and handles common errors."""
    try:
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        return {"status": "success", "message": f"Successfully updated document {document_id}."}
    except HttpError as err:
        error_message = f"An HttpError occurred: {err.reason}"
        if err.resp.status == 403:
            error_message = "Permission denied. Make sure the service account has 'Editor' access to the Google Doc."
        elif err.resp.status == 404:
            error_message = "Document not found. Please check the document_id."
        return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Markdown Processing Helpers (Refactored Logic) ---

def _handle_paragraph_style(line: str):
    """Checks a line for header markdown and returns the clean text and style."""
    if line.startswith('# '):
        return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '):
        return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '):
        return line[4:], {'namedStyleType': 'HEADING_3'}
    return line, None

def _handle_inline_styles(text: str, start_index: int):
    """Handles inline styles like bold for a given string of text, ensuring all segments have explicit styling."""
    requests = []
    matches = list(re.finditer(r'\*\*(.*?)\*\*', text))
    last_end = 0
    current_pos = start_index
    
    clean_text_len = len(re.sub(r'\*\*', '', text))

    if not matches:
        if text:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': text}})
            requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(text)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})
        return requests, len(text)

    for match in matches:
        start, end = match.span()
        plain_text_before = text[last_end:start]
        if plain_text_before:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': plain_text_before}})
            requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_text_before)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})
            current_pos += len(plain_text_before)
        
        bold_text = match.group(1)
        if bold_text:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': bold_text}})
            requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(bold_text)}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
            current_pos += len(bold_text)
        
        last_end = end

    plain_text_after = text[last_end:]
    if plain_text_after:
        requests.append({'insertText': {'location': {'index': current_pos}, 'text': plain_text_after}})
        requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_text_after)}, 'textStyle': {'bold': False}, 'fields': 'bold'}})

    return requests, clean_text_len

# --- Main Public Function (Orchestrator) ---

def process_markdown_v2(document_id: str, markdown_text: str, credentials_file_path: str) -> dict:
    """Orchestrates the conversion of a markdown string to Google Docs requests."""
    try:
        service = _get_docs_service(credentials_file_path)
        doc = service.documents().get(documentId=document_id).execute()
        
        body_content = doc.get('body', {}).get('content', [])
        start_index = 1
        if len(body_content) > 1:
            start_index = body_content[-1].get('endIndex', 1) - 1

        all_requests = []
        current_index = start_index
        lines = markdown_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            line_start_index = current_index
            
            # This is a placeholder for table handling logic to be added in the future.
            # table_requests, lines_consumed, index_offset = _handle_table(lines, i, current_index)
            # if table_requests:
            #     all_requests.extend(table_requests)
            #     current_index += index_offset
            #     i += lines_consumed
            #     continue
            
            text_to_process, paragraph_style = _handle_paragraph_style(line)
            inline_requests, inserted_len = _handle_inline_styles(text_to_process, current_index)
            all_requests.extend(inline_requests)
            current_index += inserted_len

            all_requests.append({'insertText': {'location': {'index': current_index}, 'text': '\n'}})
            current_index += 1

            if paragraph_style:
                all_requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': line_start_index, 'endIndex': current_index},
                        'paragraphStyle': paragraph_style,
                        'fields': 'namedStyleType'
                    }
                })
            
            i += 1

        if not all_requests:
            return {"status": "success", "message": "No text to append."}

        return _execute_batch_update(service, document_id, all_requests)
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Legacy function wrappers for backward compatibility ---
def append_text_to_google_doc(document_id: str, text_to_append: str, credentials_file_path: str) -> dict:
    return process_markdown_v2(document_id, text_to_append, credentials_file_path)

def clear_google_doc(document_id: str, credentials_file_path: str) -> dict:
    """Deletes all content from a Google Doc."""
    try:
        service = _get_docs_service(credentials_file_path)
        doc = service.documents().get(documentId=document_id).execute()
        body_content = doc.get('body', {}).get('content', [])
        if len(body_content) > 1:
            end_index = body_content[-1].get('endIndex', 1)
            if end_index > 2:
                requests = [{'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}}]
                return _execute_batch_update(service, document_id, requests)
        return {"status": "success", "message": "Document is already empty."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}