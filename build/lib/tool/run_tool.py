import google_docs_tool
import json
import sys

# --- Configuration ---
CREDENTIALS_FILE = 'docs-writer-credentials.json'

def main():
    """
    Reads a document ID and text content from the command line, 
    reads credentials from a file, calls the tool to append the text, 
    and prints the result.
    """
    # 1. Get Document ID and Text from command-line arguments
    if len(sys.argv) < 3:
        print("Error: Missing arguments.")
        print("Usage: python3 run_tool.py <your_document_id> \"<text_to_append>\"")
        print("Note: If your text contains spaces, you must enclose it in quotes.")
        sys.exit(1) # Exit if arguments are missing
    
    document_id = sys.argv[1]
    text_to_append = sys.argv[2]

    # 2. Read credentials and call the tool
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials_json_string = f.read()

        print(f"Attempting to append text to document: {document_id}")
        print(f"Text to append: \"{text_to_append}\"")
        
        result = google_docs_tool.append_text_to_google_doc(
            document_id=document_id,
            text_to_append=text_to_append,
            credentials_json=credentials_json_string
        )

        print("\nExecution Result:")
        print(result)

    except FileNotFoundError:
        print(f"Error: Credentials file not found at '{CREDENTIALS_FILE}'")
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")

if __name__ == '__main__':
    main()