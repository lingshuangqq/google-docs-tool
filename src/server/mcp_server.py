from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any, Optional
import argparse
import sys
import os

# --- Path Correction ---
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, SRC_PATH)

from tool import google_docs_tool
from src import auth

# --- FastAPI App ---
app = FastAPI(
    title="Google Docs MCP Tool",
    description="A server to expose Google Docs manipulation functions as an MCP tool.",
    version="1.1.0", # Version bump
)

# --- Pydantic Models ---
class AuthInfo(BaseModel):
    auth_mode: str
    creds_path: str
    token_path: Optional[str] = "token.json"

class ClearRequest(AuthInfo):
    document_id: str

class AppendMarkdownRequest(AuthInfo):
    document_id: str
    markdown_text: str

class CreateRequest(AuthInfo):
    title: str
    folder_id: Optional[str] = None

# --- Helper to get services ---
def get_services(auth_info: AuthInfo) -> Dict[str, Any]:
    if auth_info.auth_mode == 'service_account':
        return auth.get_services_with_service_account(auth_info.creds_path)
    elif auth_info.auth_mode == 'oauth':
        return auth.get_services_with_oauth(auth_info.creds_path, auth_info.token_path)
    raise HTTPException(status_code=400, detail="Invalid auth_mode specified.")

# --- API Endpoints ---

@app.post("/create-doc", summary="Create a new Google Doc")
def create_new_document(request: CreateRequest):
    try:
        services = get_services(request)
        result = google_docs_tool.create_doc(
            drive_service=services['drive'],
            title=request.title,
            folder_id=request.folder_id
        )
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/append-markdown", summary="Append markdown-formatted text to a document")
def append_markdown(request: AppendMarkdownRequest):
    try:
        services = get_services(request)
        result = google_docs_tool.process_markdown_v2(
            docs_service=services['docs'],
            document_id=request.document_id,
            markdown_text=request.markdown_text
        )
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-doc", summary="Clear all content from a document")
def clear_document(request: ClearRequest):
    try:
        services = get_services(request)
        result = google_docs_tool.clear_google_doc(
            docs_service=services['docs'],
            document_id=request.document_id
        )
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """This function is the entry point for the command-line script."""
    parser = argparse.ArgumentParser(description="Google Docs MCP Tool Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main()
