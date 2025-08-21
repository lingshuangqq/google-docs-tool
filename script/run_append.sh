#!/bin/bash

# This is an advanced script that takes command-line arguments to append text.

# Check if both document_id and text_to_append are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <document_id> \"<text_to_append>\""
    exit 1
fi

# --- Portable Paths ---
# Get the directory where the script is located.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Construct the path to the credentials file relative to the script's location.
CREDENTIALS_FILE_PATH="$SCRIPT_DIR/../credentials/docs-writer-credentials.json"

# Assign arguments to variables for clarity
DOC_ID=$1
TEXT_TO_APPEND=$2

# Dynamically create the JSON payload using printf for safety
JSON_PAYLOAD=$(printf '{
  "document_id": "%s",
  "markdown_text": "%s",
  "credentials_file_path": "%s"
}' "$DOC_ID" "$TEXT_TO_APPEND" "$CREDENTIALS_FILE_PATH")

# Make the curl request with the generated payload from stdin
echo "$JSON_PAYLOAD" | curl -X POST -H "Content-Type: application/json" -d @- http://127.0.0.1:8080/append-markdown
