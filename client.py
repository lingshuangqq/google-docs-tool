import json
import requests
import os
import sys

# --- Configuration ---
# The server URL is the only hardcoded value.
SERVER_URL = "http://127.0.0.1:8080/append-markdown"

# --- Main Execution ---
def main():
    """
    Reads a markdown file and document ID specified on the command line and calls the MCP server.
    """
    # 1. Get arguments from command-line
    if len(sys.argv) < 3:
        print("Error: Missing arguments.")
        print(f"Usage: python3 {sys.argv[0]} <document_id> <path_to_markdown_file>")
        return
    
    doc_id = sys.argv[1]
    markdown_file_path = sys.argv[2]
    
    # 2. Construct path to credentials file relative to this script's location
    script_dir = os.path.dirname(__file__)
    credentials_file = os.path.join(script_dir, ".", "credentials", "docs-writer-credentials.json")
    abs_credentials_path = os.path.abspath(credentials_file)

    print(f"Reading content from {markdown_file_path}...")
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file not found at {markdown_file_path}")
        return

    if not os.path.exists(abs_credentials_path):
        print(f"Error: Credentials file not found at {abs_credentials_path}")
        return

    # 3. Construct the request payload
    print("Constructing request payload...")
    payload = {
        "document_id": doc_id,
        "markdown_text": markdown_content,
        "credentials_file_path": abs_credentials_path
    }

    # 4. Send the request to the server
    print(f"Sending request to server at {SERVER_URL}...")
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        print("\n--- Success! ---")
        print("Server Response:")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"\n--- Error ---")
        print(f"Failed to connect to the server: {e}")
        print("Please ensure the server is running in another terminal.")

if __name__ == "__main__":
    main()
