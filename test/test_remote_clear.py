import unittest
import os
import sys

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tool import google_docs_tool
from src import auth

@unittest.skipUnless(
    os.environ.get('RUN_CLEAR_TEST') == 'true',
    "Skipping clear test. Set RUN_CLEAR_TEST=true to run it."
)
class TestRemoteClear(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for the clear test."""
        cls.doc_id_to_clear = os.environ.get('GOOGLE_DOC_ID_TO_CLEAR')
        creds_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
        
        cls.assertIsNotNone(cls.doc_id_to_clear, "GOOGLE_DOC_ID_TO_CLEAR not set in environment")
        cls.assertIsNotNone(creds_path, "GOOGLE_CREDENTIALS_PATH not set in environment")
        
        cls.services = auth.get_services_with_oauth(creds_path)
        assert 'docs' in cls.services

    def test_clear_specific_document(self):
        """Tests clearing a specific Google Doc by its ID."""
        print(f"\nAttempting to clear document: {self.doc_id_to_clear}")
        result = google_docs_tool.clear_google_doc(
            docs_service=self.services['docs'],
            document_id=self.doc_id_to_clear
        )
        self.assertEqual(result.get('status'), 'success')
