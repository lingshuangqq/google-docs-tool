import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Adjust the Python path to include the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tool import google_docs_tool

class TestGoogleDocsTool(unittest.TestCase):

    @patch('tool.google_docs_tool._get_docs_service')
    def test_process_markdown_v2_bold_and_plain(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.documents.return_value.get.return_value.execute.return_value = {
            'body': {'content': [{'endIndex': 101}]}
        }
        mock_get_service.return_value = mock_service

        document_id = "test_doc_id"
        markdown_text = "Hello **bold** world!"
        credentials_path = "/fake/path/credentials.json"
        
        google_docs_tool.process_markdown_v2(document_id, markdown_text, credentials_path)

        mock_get_service.assert_called_once_with(credentials_path)
        mock_service.documents.return_value.batchUpdate.assert_called_once()
        kwargs = mock_service.documents.return_value.batchUpdate.call_args.kwargs
        self.assertEqual(kwargs['documentId'], document_id)
        
        requests = kwargs['body']['requests']
        self.assertEqual(len(requests), 7) # 2 for each part + 1 for the final newline
        self.assertEqual(requests[0]['insertText']['text'], "Hello ")
        self.assertEqual(requests[2]['insertText']['text'], "bold")
        self.assertEqual(requests[3]['updateTextStyle']['textStyle']['bold'], True)
        self.assertEqual(requests[4]['insertText']['text'], " world!")

    @patch('tool.google_docs_tool._get_docs_service')
    def test_table_processing(self, mock_get_service):
        """
        Tests that a Markdown table is correctly parsed and converted into API requests.
        """
        mock_service = MagicMock()
        # Simulate two calls to get().execute(): one at the start, one after the table
        mock_service.documents.return_value.get.return_value.execute.side_effect = [
            {'body': {'content': [{'endIndex': 101}]}}, # Before table
            {'body': {'content': [{'endIndex': 150}]}}  # After table
        ]
        mock_get_service.return_value = mock_service

        document_id = "test_doc_id"
        markdown_text = "| Header 1 | Header 2 |\n|---|---|
| R1C1 | R1C2 |
| R2C1 | **R2C2** |"
        credentials_path = "/fake/path/credentials.json"

        google_docs_tool.process_markdown_v2(document_id, markdown_text, credentials_path)

        # Check that batchUpdate was called twice: once for the table, once for text after
        self.assertEqual(mock_service.documents.return_value.batchUpdate.call_count, 2)

        # --- Inspect the first call (table creation) ---
        first_call_args = mock_service.documents.return_value.batchUpdate.call_args_list[0]
        table_requests = first_call_args.kwargs['body']['requests']
        
        # Request 1: Insert the table structure
        self.assertIn('insertTable', table_requests[0])
        self.assertEqual(table_requests[0]['insertTable']['rows'], 3)
        self.assertEqual(table_requests[0]['insertTable']['columns'], 2)
        self.assertEqual(table_requests[0]['insertTable']['location']['index'], 100)

        # Request 2: Insert "Header 1"
        self.assertEqual(table_requests[1]['insertText']['text'], "Header 1")
        self.assertEqual(table_requests[1]['insertText']['location']['index'], 104)

        # Check last cell content for bolding
        bold_cell_request_index = -3 # (insert, style, newline)
        self.assertEqual(table_requests[bold_cell_request_index]['insertText']['text'], "R2C2")
        self.assertEqual(table_requests[bold_cell_request_index + 1]['updateTextStyle']['textStyle']['bold'], True)

        # --- Inspect the second call (after table) ---
        second_call_args = mock_service.documents.return_value.batchUpdate.call_args_list[1]
        after_table_requests = second_call_args.kwargs['body']['requests']
        # This should just be a newline character
        self.assertEqual(len(after_table_requests), 1)
        self.assertEqual(after_table_requests[0]['insertText']['text'], '\n')

if __name__ == '__main__':
    unittest.main()