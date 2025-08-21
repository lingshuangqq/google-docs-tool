from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any
import argparse
import sys
import os

# --- Absolute Path Correction ---
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, SRC_PATH)

from tool import google_docs_tool

# --- FastAPI App ---
app = FastAPI(
    title="Google Docs MCP Tool",
    description="A server to expose Google Docs manipulation functions as an MCP tool.",
    version="1.0.0",
)

# --- Pydantic Models ---
class DocRequestBase(BaseModel):
    document_id: str
    credentials_file_path: str

class MarkdownAppendRequest(DocRequestBase):
    markdown_text: str

# --- API Endpoints ---
@app.post("/append-markdown", summary="Append markdown-formatted text to a document")
def append_markdown(request: MarkdownAppendRequest):
    result = google_docs_tool.process_markdown_v2(
        document_id=request.document_id,
        markdown_text=request.markdown_text,
        credentials_file_path=request.credentials_file_path
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

def main():
    """This function is the entry point for the command-line script."""
    parser = argparse.ArgumentParser(description="Google Docs MCP Tool Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main()
