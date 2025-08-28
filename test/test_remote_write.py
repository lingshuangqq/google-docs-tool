import unittest
import os
import sys
import time

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tool import google_docs_tool
from src import auth

# --- Remote Integration Tests ---
@unittest.skipUnless(
    os.environ.get('RUN_INTEGRATION_TESTS') == 'true',
    "Skipping integration tests. Set RUN_INTEGRATION_TESTS=true to run them."
)
class TestRemoteWriteAndAppend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for the entire class."""
        cls.doc_id = os.environ.get('GOOGLE_DOC_ID')
        cls.folder_id = os.environ.get('GOOGLE_FOLDER_ID')
        creds_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
        
        cls.assertIsNotNone(cls.doc_id, "GOOGLE_DOC_ID not set in environment")
        cls.assertIsNotNone(creds_path, "GOOGLE_CREDENTIALS_PATH not set in environment")
        
        cls.services = auth.get_services_with_oauth(creds_path)
        assert 'docs' in cls.services
        assert 'drive' in cls.services

    def test_A_overwrite_doc(self):
        """Tests overwriting a doc. Runs first."""
        result = google_docs_tool.write_to_google_doc(
            docs_service=self.services['docs'],
            drive_service=self.services['drive'],
            markdown_content="# Initial Content",
            document_id=self.doc_id
        )
        self.assertEqual(result.get('status'), 'success')

    def test_B_append_to_existing_doc(self):
        """Tests appending to a doc. Runs second."""
        time.sleep(2) # Avoid rate limiting
        result = google_docs_tool.append_to_google_doc(
            docs_service=self.services['docs'],
            document_id=self.doc_id,
            markdown_content="## Appended Content"
        )
        self.assertEqual(result.get('status'), 'success')

    def test_C_create_new_doc_in_folder(self):
        """Tests creating a new doc in a specific folder. Runs last."""
        self.assertIsNotNone(self.folder_id, "GOOGLE_FOLDER_ID not set for this test")
        time.sleep(2) # Avoid rate limiting
        result = google_docs_tool.write_to_google_doc(
            docs_service=self.services['docs'],
            drive_service=self.services['drive'],
            markdown_content="# This is a new document in a specific folder.",
            title="Specific Folder Test Doc",
            folder_id=self.folder_id
        )
        self.assertEqual(result.get('status'), 'success')
        self.assertIn('document_id', result)

    def test_D_create_doc_with_all_formats_in_folder(self):
        """Tests creating a new doc with complex content in a specific folder."""
        self.assertIsNotNone(self.folder_id, "GOOGLE_FOLDER_ID not set for this test")
        time.sleep(2) # Avoid rate limiting

        markdown_content = (
            "# All Formats Test in Folder\n\n"
            "This document serves as a comprehensive test of the markdown conversion.\n\n"
            "## Sub-heading with **bold** text\n\n"
            "- Unordered List Item 1\n"
            "- Unordered List Item 2\n"
            "  - Nested Item A\n"
            "  - Nested Item B\n"
            "- Unordered List Item 3\n"
        )

        result = google_docs_tool.write_to_google_doc(
            docs_service=self.services['docs'],
            drive_service=self.services['drive'],
            markdown_content=markdown_content,
            title="All Formats In-Folder Test",
            folder_id=self.folder_id
        )
        self.assertEqual(result.get('status'), 'success')
        self.assertIn('document_id', result)

if __name__ == '__main__':
    unittest.main()