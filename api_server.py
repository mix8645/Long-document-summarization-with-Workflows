import uvicorn
import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional  # Import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN not found in the .env file")

# Import service functions
from summarizer_service import summarize_from_file, summarize_from_content_chunks

# --- Security Scheme ---
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency function to verify the bearer token."""
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing authentication token",
        )
    return True

# --- Pydantic Models ---
class MetadataModel(BaseModel):
    file_name: str
    source_url: str
    tags: str

class ChunkModel(BaseModel):
    metadata: MetadataModel
    score: int
    content: str

class InputModel(BaseModel):
    success: bool
    query: Optional[str] = None
    data: List[ChunkModel]


# --- FastAPI App ---
app = FastAPI(
    title="MapReduce Summarization API",
    description="An API to summarize long documents using a MapReduce approach with Gemini AI.",
    version="1.0.0"
)

# --- Endpoints ---
@app.post("/summarize/json/", tags=["Summarization"], dependencies=[Depends(verify_token)])
async def summarize_via_json_body(request_data: InputModel):
    """Endpoint to receive and process a JSON body for summarization."""
    try:
        chunks_content = [item.content for item in request_data.data]
        user_query = request_data.query  # Extract the user's query

        if not chunks_content:
            raise HTTPException(status_code=400, detail="No 'content' data found in JSON body")

        print(f"Received JSON with {len(chunks_content)} chunks and query: '{user_query}'")
        # Pass the query to the service function
        summary = await summarize_from_content_chunks(chunks_content, query=user_query)
        
        if summary.startswith("An error occurred"):
            raise HTTPException(status_code=500, detail=summary)
            
        return {"input_type": "json_body", "query": user_query, "summary": summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")


@app.post("/summarize/file/", tags=["Summarization"], dependencies=[Depends(verify_token)])
async def summarize_via_file_upload(
    file: UploadFile = File(...), 
    query: Optional[str] = Form(None) # Also allow query for file uploads
):
    """Endpoint to receive and process a JSON file upload for summarization."""
    if file.content_type != 'application/json':
        raise HTTPException(status_code=400, detail="Uploaded file must be of type application/json")

    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"Received file: {file.filename} and query: '{query}'")
        # Pass the query to the service function
        summary = await summarize_from_file(temp_file_path, query=query)
        
        if summary.startswith("Error"):
             raise HTTPException(status_code=500, detail=summary)

        return {"input_type": "file_upload", "filename": file.filename, "query": query, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Main Execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)