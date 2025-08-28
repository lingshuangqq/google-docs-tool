#!/bin/bash

# A master script to run tests, providing a CLI interface for configuration.

# --- Default values ---
RUN_ONLINE="false"
DOC_ID=""
CREDS_PATH=""
FOLDER_ID=""
RUN_CLEAR_TEST="false"
CLEAR_DOC_ID=""

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --online) RUN_ONLINE="true";;
        --doc-id) DOC_ID="$2"; shift;;
        --creds-path) CREDS_PATH="$2"; shift;;
        --folder-id) FOLDER_ID="$2"; shift;;
        --run-clear-test) RUN_CLEAR_TEST="true";;
        --clear-doc-id) CLEAR_DOC_ID="$2"; shift;;
        -h|--help)
            # ... (help message remains the same)
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1;;
    esac
    shift
done

# --- Test Execution Logic ---

# On-demand clear test
if [ "$RUN_CLEAR_TEST" = "true" ]; then
    echo "--- Running ON-DEMAND clear test ---"
    if [ -z "$CLEAR_DOC_ID" ] || [ -z "$CREDS_PATH" ]; then
        echo "Error: --run-clear-test requires --clear-doc-id and --creds-path to be set." >&2
        exit 1
    fi
    export RUN_CLEAR_TEST="true"
    export GOOGLE_DOC_ID_TO_CLEAR="$CLEAR_DOC_ID"
    export GOOGLE_CREDENTIALS_PATH="$CREDS_PATH"
    # Execute only the specific clear test file
    python3 -m unittest test/test_remote_clear.py
    exit 0 # Exit after the specific test is run
fi

# Standard online integration tests
if [ "$RUN_ONLINE" = "true" ]; then
    echo "--- Running ONLINE integration tests ---"
    if [ -z "$DOC_ID" ] || [ -z "$CREDS_PATH" ]; then
        echo "Error: --online flag requires --doc-id and --creds-path to be set." >&2
        exit 1
    fi
    export RUN_INTEGRATION_TESTS="true"
    export GOOGLE_DOC_ID="$DOC_ID"
    export GOOGLE_CREDENTIALS_PATH="$CREDS_PATH"
    if [ -n "$FOLDER_ID" ]; then
        export GOOGLE_FOLDER_ID="$FOLDER_ID"
    fi
    # Discover and run all tests that are not explicitly skipped
    python3 -m unittest discover test
    exit 0
fi

# Default: Run local mock tests
echo "--- Running LOCAL mock tests ---"
python3 -m unittest discover test