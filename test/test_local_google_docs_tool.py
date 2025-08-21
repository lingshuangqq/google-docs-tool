import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust the Python path to include the 'src' directory
# This allows us to import the module we want to test
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Now we can import the tool module
from tool import google_docs_tool

class TestGoogleDocsTool(unittest.TestCase):

    # Use the @patch decorator to replace the real _get_docs_service function
    # with a mock during the test.
    @patch('tool.google_docs_tool._get_docs_service')
    def test_append_formatted_text_bold_and_plain(self, mock_get_service):
        """
        Tests the append_formatted_text function to ensure it creates the correct
        API requests for a mix of bold and plain text.
        """
        # --- Setup ---
        # Create a mock for the entire Google Docs service object
        mock_service = MagicMock()
        
        # Configure the mock for the .documents().get().execute() call chain
        # This simulates fetching the document's current state
        mock_service.documents.return_value.get.return_value.execute.return_value = {
            'body': {'content': [{'endIndex': 101}]}
        }
        
        # Make our patched function return our mock service
        mock_get_service.return_value = mock_service

        # --- Action ---
        # Call the function we are testing
        document_id = "test_doc_id"
        markdown_text = "Hello **bold** world!"
        credentials_path = "/fake/path/credentials.json"
        
        google_docs_tool.append_formatted_text(document_id, markdown_text, credentials_path)

        # --- Assertions ---
        # 1. Check that we tried to get the service with the correct credentials path
        mock_get_service.assert_called_once_with(credentials_path)

        # 2. Check that we called the batchUpdate method once
        mock_service.documents.return_value.batchUpdate.assert_called_once()

        # 3. Inspect the `requests` list that was passed to batchUpdate
        kwargs = mock_service.documents.return_value.batchUpdate.call_args.kwargs
        self.assertEqual(kwargs['documentId'], document_id)
        
        requests = kwargs['body']['requests']
        
        # We expect 6 requests for "Hello **bold** world!" because it's split into 3 parts
        # and each part gets an Insert and an UpdateStyle request.
        self.assertEqual(len(requests), 6)

        # Check Request 1: Insert "Hello "
        self.assertEqual(requests[0]['insertText']['text'], "Hello ")
        self.assertEqual(requests[0]['insertText']['location']['index'], 100)

        # Check Request 2: Style "Hello " as non-bold
        self.assertEqual(requests[1]['updateTextStyle']['range']['startIndex'], 100)
        self.assertEqual(requests[1]['updateTextStyle']['range']['endIndex'], 106)
        self.assertEqual(requests[1]['updateTextStyle']['textStyle']['bold'], False)

        # Check Request 3: Insert "bold"
        self.assertEqual(requests[2]['insertText']['text'], "bold")
        self.assertEqual(requests[2]['insertText']['location']['index'], 106)

        # Check Request 4: Style "bold" as bold
        self.assertEqual(requests[3]['updateTextStyle']['range']['startIndex'], 106)
        self.assertEqual(requests[3]['updateTextStyle']['range']['endIndex'], 110)
        self.assertEqual(requests[3]['updateTextStyle']['textStyle']['bold'], True)

        # Check Request 5: Insert " world!"
        self.assertEqual(requests[4]['insertText']['text'], " world!")
        self.assertEqual(requests[4]['insertText']['location']['index'], 110)

        # Check Request 6: Style " world!" as non-bold
        self.assertEqual(requests[5]['updateTextStyle']['range']['startIndex'], 110)
        self.assertEqual(requests[5]['updateTextStyle']['range']['endIndex'], 117)
        self.assertEqual(requests[5]['updateTextStyle']['textStyle']['bold'], False)


if __name__ == '__main__':
    unittest.main()
