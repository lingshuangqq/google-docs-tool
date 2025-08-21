import unittest
import os
import sys

# Adjust the Python path to include the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tool import google_docs_tool

# --- Configuration for Integration Tests ---
# We read the configuration from environment variables.
# This is safer than hardcoding secrets or paths in the code.
DOCUMENT_ID = os.environ.get("GOOGLE_DOC_ID")
CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")
RUN_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS", "false").lower() == "true"

# A reason to skip the tests if the required environment variables are not set.
SKIP_REASON = "Integration test environment variables (RUN_INTEGRATION_TESTS, GOOGLE_DOC_ID, GOOGLE_CREDENTIALS_PATH) are not set."

# The @unittest.skipUnless decorator will skip these tests unless the condition is met.
@unittest.skipUnless(RUN_INTEGRATION_TESTS and DOCUMENT_ID and CREDENTIALS_PATH, SKIP_REASON)
class TestIntegrationGoogleDocsTool(unittest.TestCase):

    def test_append_formatted_text_online(self):
        """
        This is an integration test. It makes a REAL API call to Google Docs.
        It requires a valid document ID and credentials file path to be set
        in environment variables.
        """
        # The text we will try to append.
        markdown_text = "\n--- Integration Test Run ---\nThis is a **bold** message from the integration test.\n"

        # Call the actual function.
        result = google_docs_tool.append_formatted_text(
            document_id=DOCUMENT_ID,
            markdown_text=markdown_text,
            credentials_file_path=CREDENTIALS_PATH
        )

        # For an integration test, we just want to confirm that the API call
        # was successful. We don't need to read the content back.
        self.assertEqual(result.get("status"), "success", f"API call failed with message: {result.get('message')}")
        print(f"\nSuccessfully appended test text to document: {DOCUMENT_ID}")


if __name__ == '__main__':
    # This allows running the test file directly.
    unittest.main()
