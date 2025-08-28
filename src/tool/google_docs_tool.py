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
        return {"status": "error", "message": f"An HttpError occurred: {err.reason}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Markdown Parsing and Request Generation ---

def _get_markdown_requests(markdown_text: str, start_index: int):
    """Converts a markdown string into a list of Google Docs API requests starting at a given index."""
    all_requests = []
    current_index = start_index
    lines = markdown_text.split('\n')

    for line in lines:
        line_start_index = current_index
        
        # 1. Handle Paragraph Styles (Headers, Lists)
        # This part can be extended with more markdown features like tables.
        indent_level, list_text, bullet_char = _handle_list_item(line)
        if list_text is not None:
            text_to_process = bullet_char + ' ' + list_text
            paragraph_style = {
                'indentFirstLine': {'magnitude': 18 * (indent_level + 1), 'unit': 'PT'},
                'indentStart': {'magnitude': 36 * (indent_level + 1), 'unit': 'PT'}
            }
            paragraph_fields = 'indentStart,indentFirstLine'
        else:
            text_to_process, header_style = _handle_paragraph_style(line)
            paragraph_style = header_style
            paragraph_fields = 'namedStyleType'

        # 2. Handle Inline Styles (Bold)
        inline_requests, inserted_len = _handle_inline_styles(text_to_process, current_index)
        all_requests.extend(inline_requests)
        current_index += inserted_len

        # 3. Add newline and apply paragraph style
        all_requests.append({'insertText': {'location': {'index': current_index}, 'text': '\n'}})
        current_index += 1
        if paragraph_style:
            all_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': line_start_index, 'endIndex': current_index},
                    'paragraphStyle': paragraph_style,
                    'fields': paragraph_fields
                }
            })

    return all_requests

def _handle_paragraph_style(line: str):
    if line.startswith('# '): return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '): return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '): return line[4:], {'namedStyleType': 'HEADING_3'}
    if line.startswith('#### '): return line[5:], {'namedStyleType': 'HEADING_4'}
    return line, None

def _handle_list_item(line: str):
    match = re.match(r'^(\s*)(\*|-)\s+(.*)', line)
    if not match: return None, None, None
    indent_str, text = match.group(1), match.group(3)
    indent_level = len(indent_str) // 2
    bullet_chars = ['\u25CF', '\u25CB', '\u25A0']
    bullet_char = bullet_chars[indent_level % len(bullet_chars)]
    return indent_level, text, bullet_char

def _handle_inline_styles(text: str, start_index: int):
    requests = []
    matches = list(re.finditer(r'\*\*(.*?)\*\*', text))
    last_end, current_pos = 0, start_index
    clean_text_len = len(re.sub(r'\*\*', '', text))

    if not matches:
        if text: requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': text}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(text)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
        return requests, len(text)

    for match in matches:
        start, end = match.span()
        # Plain text before bold
        plain_before = text[last_end:start]
        if plain_before:
            requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': plain_before}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_before)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
            current_pos += len(plain_before)
        # Bold text
        bold_text = match.group(1)
        if bold_text:
            requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': bold_text}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(bold_text)}, 'textStyle': {'bold': True}, 'fields': 'bold'}}])
            current_pos += len(bold_text)
        last_end = end
    # Plain text after last bold
    plain_after = text[last_end:]
    if plain_after:
        requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': plain_after}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_after)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
    return requests, clean_text_len

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

def write_to_google_doc(docs_service, drive_service, markdown_content: str, title: str = "Untitled Document", document_id: str = None, folder_id: str = None) -> dict:
    """
    Writes markdown content to a Google Doc. Creates a new doc if document_id is not provided.
    
    Args:
        docs_service: Authorized Google Docs service object.
        drive_service: Authorized Google Drive service object.
        markdown_content (str): The markdown text to write.
        title (str): The title for a new document.
        document_id (str, optional): The ID of an existing document.
        folder_id (str, optional): The ID of a parent folder for a new document.

    Returns:
        A dictionary with the status and message.
    """
    try:
        # 1. Create a new document if no ID is provided
        if not document_id:
            print("No document ID provided, creating a new document...")
            creation_result = create_doc(drive_service, title, folder_id)
            if creation_result["status"] == "error":
                return creation_result # Propagate the error
            document_id = creation_result["document_id"]
            print(f"Successfully created new document with ID: {document_id}")
        
        # 2. Clear the document before writing new content
        print(f"Clearing document {document_id} before writing...")
        clear_result = clear_google_doc(docs_service, document_id)
        if clear_result["status"] == "error":
            # Don't stop for a clear error, just log it. The doc might be empty.
            print(f"Warning: Could not clear document. {clear_result['message']}")

        # 3. Get markdown conversion requests
        print("Converting markdown to Google Docs format...")
        # The document is now empty, so we start writing at index 1
        requests = _get_markdown_requests(markdown_content, start_index=1)

        # 4. Execute the batch update to write the content
        print("Writing content to the document...")
        write_result = _execute_batch_update(docs_service, document_id, requests)
        
        if write_result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully wrote content to document {document_id}.",
                "document_id": document_id
            }
        else:
            return write_result

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during the write process: {e}"}
