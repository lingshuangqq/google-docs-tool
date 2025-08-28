import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tool import markdown_parser

class TestMarkdownParser(unittest.TestCase):

    def test_heading_1(self):
        """Tests conversion of a level 1 heading."""
        md = "# Hello World"
        requests = markdown_parser.get_markdown_requests(md, 1)
        self.assertIn({
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': 13},
                'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                'fields': 'namedStyleType'
            }
        }, requests)
        self.assertIn({'insertText': {'location': {'index': 1}, 'text': 'Hello World'}}, requests)

    def test_bold_text(self):
        """Tests conversion of bold text."""
        md = "This is **bold** text."
        requests = markdown_parser.get_markdown_requests(md, 1)
        self.assertIn({
            'updateTextStyle': {
                'range': {'startIndex': 9, 'endIndex': 13},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }
        }, requests)
        self.assertIn({'insertText': {'location': {'index': 1}, 'text': 'This is '}}, requests)
        self.assertIn({'insertText': {'location': {'index': 13}, 'text': ' text.'}}, requests)

    def test_simple_list(self):
        """Tests a simple unordered list."""
        md = "* One\n* Two"
        requests = markdown_parser.get_markdown_requests(md, 1)
        # Expected: '● One\n' -> range 1-7. Then '● Two\n' -> range 7-13
        self.assertIn({
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': 7},
                'paragraphStyle': {
                    'indentFirstLine': {'magnitude': 18, 'unit': 'PT'},
                    'indentStart': {'magnitude': 36, 'unit': 'PT'}
                },
                'fields': 'indentStart,indentFirstLine'
            }
        }, requests)
        self.assertIn({
            'updateParagraphStyle': {
                'range': {'startIndex': 7, 'endIndex': 13},
                'paragraphStyle': {
                    'indentFirstLine': {'magnitude': 18, 'unit': 'PT'},
                    'indentStart': {'magnitude': 36, 'unit': 'PT'}
                },
                'fields': 'indentStart,indentFirstLine'
            }
        }, requests)

    def test_nested_list(self):
        """Tests a nested unordered list."""
        md = "* Parent\n  * Child"
        requests = markdown_parser.get_markdown_requests(md, 1)
        # Expected: '● Parent\n' -> range 1-10. Then '○ Child\n' -> range 10-18
        self.assertIn({
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': 10},
                'paragraphStyle': {
                    'indentFirstLine': {'magnitude': 18, 'unit': 'PT'},
                    'indentStart': {'magnitude': 36, 'unit': 'PT'}
                },
                'fields': 'indentStart,indentFirstLine'
            }
        }, requests)
        self.assertIn({
            'updateParagraphStyle': {
                'range': {'startIndex': 10, 'endIndex': 18},
                'paragraphStyle': {
                    'indentFirstLine': {'magnitude': 36, 'unit': 'PT'},
                    'indentStart': {'magnitude': 72, 'unit': 'PT'}
                },
                'fields': 'indentStart,indentFirstLine'
            }
        }, requests)

if __name__ == '__main__':
    unittest.main()