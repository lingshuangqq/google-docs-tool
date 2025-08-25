import argparse
import sys
import os
import json
import requests

# Adjust path to import from the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))

from tool import google_docs_tool
from src import auth

# --- Configuration ---
SERVER_BASE_URL = "http://127.0.0.1:8080"

# --- Helper Functions ---
def get_services(args):
    """Authenticates and returns the docs and drive service objects."""
    print(f"Attempting authentication using '{args.auth}' mode...")
    try:
        if args.auth == 'service_account':
            return auth.get_services_with_service_account(args.creds_path)
        elif args.auth == 'oauth':
            return auth.get_services_with_oauth(args.creds_path, args.token_path)
    except Exception as e:
        print(f"\n--- Authentication Error ---")
        print(f"Failed to create an authorized service: {e}")
        sys.exit(1)

def read_markdown_file(file_path):
    """Reads content from the specified markdown file."""
    print(f"Reading content from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file not found at {file_path}")
        sys.exit(1)

# --- Command Handlers ---
def handle_write(args):
    """Handles the logic for the 'write' command."""
    services = get_services(args)
    markdown_content = read_markdown_file(args.markdown_file)
    target_doc_id = args.doc_id

    if not target_doc_id:
        print(f"No document ID provided. Creating a new document with title: '{args.title}'")
        create_result = google_docs_tool.create_doc(services['drive'], args.title, args.folder_id)
        if create_result.get("status") == "error":
            print(f"\n--- Document Creation Error ---\n{create_result.get('message')}")
            return
        target_doc_id = create_result.get("document_id")
        print(f"Successfully created new document with ID: {target_doc_id}")

    print(f"Writing content to document ID: {target_doc_id}...")
    write_result = google_docs_tool.process_markdown_v2(services['docs'], target_doc_id, markdown_content)
    if write_result.get("status") == "success":
        print("\n--- Success! ---")
        print(write_result.get("message"))
    else:
        print(f"\n--- Tool Error---\n{write_result.get('message')}")

def handle_clear(args):
    """Handles the logic for the 'clear' command."""
    services = get_services(args)
    print(f"Clearing content from document ID: {args.doc_id}...")
    result = google_docs_tool.clear_google_doc(services['docs'], args.doc_id)
    if result.get("status") == "success":
        print("\n--- Success! ---")
        print(result.get("message"))
    else:
        print(f"\n--- Tool Error---\n{result.get('message')}")

def handle_replace_markdown(args):
    """Handles the logic for the 'replace-markdown' command."""
    services = get_services(args)
    replacements = {p: f for p, f in args.replace}
    print(f"Building replacements map...")
    for placeholder, filepath in replacements.items():
        replacements[placeholder] = read_markdown_file(filepath)
    
    print(f"Replacing placeholders in document ID: {args.doc_id}...")
    result = google_docs_tool.replace_markdown_placeholders(services['docs'], args.doc_id, replacements)
    
    if result.get("status") == "success":
        print("\n--- Success! ---")
        print(result.get("message"))
    else:
        print(f"\n--- Tool Error---\n{result.get("message")}")

# --- Main Function ---
def main():
    """Main function to parse subcommands and arguments."""
    parser = argparse.ArgumentParser(description="A client for the Google Docs tool.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    auth_parser = argparse.ArgumentParser(add_help=False)
    auth_parser.add_argument("--auth", type=str, choices=['service_account', 'oauth'], required=True, help="Authentication method.")
    auth_parser.add_argument("--creds-path", type=str, required=True, help="Path to credentials JSON file.")
    auth_parser.add_argument("--token-path", default="credentials/token.json", help="(For OAuth) Path to store the token.json file.")

    parser_write = subparsers.add_parser('write', help='Write a markdown file to a new or existing Google Doc.', parents=[auth_parser])
    parser_write.add_argument("markdown_file", help="The path to the local markdown file.")
    write_group = parser_write.add_mutually_exclusive_group(required=True)
    write_group.add_argument("--doc-id", help="The ID of an EXISTING Google Doc to append to.")
    write_group.add_argument("--title", help="The title for a NEW Google Doc to be created.")
    parser_write.add_argument("--folder-id", help="(Optional) The Google Drive Folder ID for the new document.")
    parser_write.set_defaults(func=handle_write)

    parser_clear = subparsers.add_parser('clear', help='Clear all content from a specified Google Doc.', parents=[auth_parser])
    parser_clear.add_argument("doc_id", help="The ID of the Google Doc to clear.")
    parser_clear.set_defaults(func=handle_clear)

    parser_replace = subparsers.add_parser('replace-markdown', help='Replace one or more placeholders with formatted markdown from files.', parents=[auth_parser])
    parser_replace.add_argument("doc_id", help="The ID of the Google Doc to edit.")
    parser_replace.add_argument('--replace', nargs=2, metavar=('PLACEHOLDER', 'FILE_PATH'), action='append', required=True, help="Specify a placeholder and the markdown file to replace it with. Can be used multiple times.")
    parser_replace.set_defaults(func=handle_replace_markdown)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()