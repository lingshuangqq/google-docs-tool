#!/bin/bash

# A master script to run tests, providing a CLI interface for configuration.

# Default values
RUN_ONLINE="false"
DOC_ID=""
CREDS_PATH=""

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --online) RUN_ONLINE="true";;
        --doc-id) DOC_ID="$2"; shift;;
        --creds-path) CREDS_PATH="$2"; shift;;
        -h|--help)
            echo "Usage: $0 [--online] [--doc-id <id>] [--creds-path <path>]"
            echo ""
            echo "Runs tests for the Google Docs tool."
            echo ""
            echo "Options:"
            echo "  --online        Run the online integration tests. Requires --doc-id and --creds-path."
            echo "  --doc-id        The Google Doc ID to use for online tests."
            echo "  --creds-path    The path to the credentials JSON file for online tests."
            echo "  -h, --help      Show this help message."
            echo ""
            echo "If --online is not specified, only local mock tests will be run."
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1;;
    esac
    shift
done

# --- Test Execution ---

# If running online tests, set the required environment variables
if [ "$RUN_ONLINE" = "true" ]; then
    echo "--- Running ONLINE integration tests ---"
    if [ -z "$DOC_ID" ] || [ -z "$CREDS_PATH" ]; then
        echo "Error: --online flag requires --doc-id and --creds-path to be set."
        exit 1
    fi
    
    export RUN_INTEGRATION_TESTS="true"
    export GOOGLE_DOC_ID="$DOC_ID"
    export GOOGLE_CREDENTIALS_PATH="$CREDS_PATH"
    
else
    echo "--- Running LOCAL mock tests ---"
    # Unset the variables just in case they were set in the shell before
    unset RUN_INTEGRATION_TESTS
    unset GOOGLE_DOC_ID
    unset GOOGLE_CREDENTIALS_PATH
fi

# Run the unittest discovery
# It will automatically run local tests and skip online tests unless the env vars are set
python3 -m unittest discover test
