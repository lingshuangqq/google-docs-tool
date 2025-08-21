#!/bin/bash

# This script takes command-line arguments to append MARKDOWN text.

# Check if both document_id and markdown_text are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <document_id> \"<markdown_text>\""
    echo "Example: $0 your_doc_id \"# A Title\nAnd some **bold** text.\""
    exit 1
fi

# --- Portable Paths ---
# Get the directory where the script is located.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Construct the path to the credentials file relative to the script's location.
CREDENTIALS_FILE_PATH="$SCRIPT_DIR/../credentials/docs-writer-credentials.json"

# Assign arguments to variables for clarity
DOC_ID=$1
MARKDOWN_TEXT=$2

# Dynamically create the JSON payload
JSON_PAYLOAD=$(printf '{
  "document_id": "%s",
  "markdown_text": "%s",
  "credentials_file_path": "%s"
}' "$DOC_ID" "$MARKDOWN_TEXT" "$CREDENTIALS_FILE_PATH")

# Make the curl request to the new endpoint
echo "$JSON_PAYLOAD" | curl -X POST -H "Content-Type: application/json" -d @- http://127.0.0.1:8080/append-markdown