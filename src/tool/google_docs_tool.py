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
    creds = Credentials.from_service_account_file(credentials_file_path, scopes=SCOPES)
    return build("docs", "v1", credentials=creds)

def _execute_batch_update(service, document_id: str, requests: list) -> dict:
    if not requests:
        return {"status": "success", "message": "No requests to execute."}
    try:
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        return {"status": "success", "message": f"Successfully updated document {document_id}."}
    except HttpError as err:
        return {"status": "error", "message": f"An HttpError occurred: {err.reason}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Markdown Processing Helpers ---

def _handle_paragraph_style(line: str):
    if line.startswith('# '):
        return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '):
        return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '):
        return line[4:], {'namedStyleType': 'HEADING_3'}
    return line, None

def _handle_inline_styles(text: str, start_index: int):
    requests = []
    parts = re.split(r'(\*\*.*?\*\*)', text)
    current_pos = start_index
    total_len = 0

    for part in parts:
        if not part:
            continue
        is_bold = part.startswith('**') and part.endswith('**')
        content = part.strip('*') if is_bold else part
        content_len = len(content)

        if content:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': content}})
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': current_pos, 'endIndex': current_pos + content_len},
                    'textStyle': {'bold': is_bold},
                    'fields': 'bold'
                }
            })
            current_pos += content_len
            total_len += content_len
            
    return requests, total_len

def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('|') and stripped.endswith('|') and not re.match(r'^\|[:\-s|]+$', stripped)

def _is_table_separator(line: str) -> bool:
    return re.match(r'^\|[:\-s|]+$', line.strip()) is not None

def _parse_table_row(line: str) -> list[str]:
    if not line.strip():
        return []
    return [cell.strip() for cell in line.strip().strip('|').split('|')]

def _handle_table(table_lines: list[str], start_index: int):
    if not table_lines:
        return [], 0

    header_cells = _parse_table_row(table_lines[0])
    num_columns = len(header_cells)
    data_rows_content = [_parse_table_row(line) for line in table_lines[1:]]
    num_rows = len(data_rows_content) + 1

    requests = [{'insertTable': {'location': {'index': start_index},'rows': num_rows,'columns': num_columns}}]

    current_pos = start_index + 4
    total_inserted_len = 0

    all_rows = [header_cells] + data_rows_content

    for row in all_rows:
        while len(row) < num_columns:
            row.append("")
        row = row[:num_columns]

        for cell_text in row:
            inline_reqs, inserted_len = _handle_inline_styles(cell_text, current_pos)
            requests.extend(inline_reqs)
            current_pos += inserted_len
            total_inserted_len += inserted_len
            current_pos += 2

    final_len = total_inserted_len + (num_rows * num_columns * 2) + 2
    return requests, final_len

# --- Main Public Function (Orchestrator) ---
def process_markdown_v2(document_id: str, markdown_text: str, credentials_file_path: str) -> dict:
    try:
        service = _get_docs_service(credentials_file_path)
        doc = service.documents().get(documentId=document_id).execute() 
        
        body_content = doc.get('body', {}).get('content', [])
        start_index = 1
        if body_content and body_content[-1].get('endIndex'):
            start_index = body_content[-1].get('endIndex') - 1

        all_requests = []
        current_index = start_index
        lines = markdown_text.split('\n')
        
        table_buffer = []

        def flush_table_buffer():
            nonlocal current_index, all_requests, service, doc
            if table_buffer:
                if all_requests:
                    _execute_batch_update(service, document_id, all_requests)
                    all_requests = []
                
                doc = service.documents().get(documentId=document_id).execute()
                current_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1) -1

                table_reqs, _ = _handle_table(table_buffer, current_index)
                _execute_batch_update(service, document_id, table_reqs)

                doc = service.documents().get(documentId=document_id).execute()
                current_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1) - 1

                table_buffer.clear()

        for line in lines:
            if _is_table_separator(line):
                continue

            if _is_table_line(line):
                table_buffer.append(line)
            else:
                flush_table_buffer()
                
                line_start_index = current_index
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

        flush_table_buffer()

        return _execute_batch_update(service, document_id, all_requests)

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}
