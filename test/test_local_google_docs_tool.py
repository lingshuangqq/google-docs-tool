import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Adjust the Python path to include the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tool import google_docs_tool

class TestGoogleDocsTool(unittest.TestCase):
    pass

    

    

if __name__ == '__main__':
    unittest.main()