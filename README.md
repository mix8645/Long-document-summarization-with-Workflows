# MapReduce Summarization API 🤖

A FastAPI-based API that summarizes long documents using a MapReduce approach with Google's Gemini AI.

## 🚀 Features

- **FastAPI REST API**: High-performance asynchronous API server.
- **MapReduce Logic**: Implements a MapReduce pattern to handle documents of any length by breaking them into batches.
- **Query-Aware Summarization**: Can perform a general executive summary or a focused summary based on a user's specific query.
- **Asynchronous Batch Processing**: Uses `asyncio` to process multiple document batches in parallel, speeding up the "Map" phase.
- **LLM Integration**: Leverages Google's Gemini (`gemini-2.5-flash`) for both batch summarization and the final "Reduce" step.
- **Secure**: Endpoints are protected by Bearer Token authentication.
- **Dual Input Methods**: Accepts input via a direct JSON body (`/summarize/json/`) or a JSON file upload (`/summarize/file/`).

## 📋 Prerequisites

- Python 3.x
- A Google API Key
- A secure Bearer Token

## 🛠️ Technology Stack

- **Framework:** FastAPI
- **LLM:** Google Gemini (`gemini-2.5-flash`)
- **Language:** Python
- **Async:** `asyncio`
- **Server:** `uvicorn`
- **Libraries:** `pydantic`, `python-dotenv`, `google-generativeai`

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd LONG-DOCUMENT-SUMMARIZATION
````

### 2\. Install dependencies

```bash
pip install fastapi "uvicorn[standard]" google-generativeai python-dotenv
```

### 3\. Configure environment variables

Create a `.env` file in the root directory:

```env
# Google API Key for Gemini
GOOGLE_API_KEY=your_google_api_key_here

# API Token for Bearer Authentication
BEARER_TOKEN=your-secret-token-here
```

## 🚦 Running the Application

### Local Development

Run the API server using Uvicorn. The file to run is `api_server.py`.

```bash
# Run the server
uvicorn api_server:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## 📡 API Endpoints

### Base URL

```
[http://127.0.0.1:8000](http://127.0.0.1:8000)
```

### Protected Endpoints (Requires Authentication)

All summarization endpoints require an `Authorization` header:
`Authorization: Bearer your-secret-token-here`

-----

#### 1\. Summarize via JSON Body

```http
POST /summarize/json/
```

This endpoint accepts a JSON body matching the `InputModel`. The `query` field in the JSON is optional.

**Headers:**

```
Content-Type: application/json
Authorization: Bearer your-secret-token-here
```

**Request Body:**

```json
{
  "success": true,
  "query": "What papers talk about RAG?",
  "data": [
    {
      "metadata": {
        "file_name": "llm_paper_1.pdf",
        "source_url": "[https://arxiv.org/abs/2301.00001](https://arxiv.org/abs/2301.00001)",
        "tags": "LLM,scaling,transformers,AI,research"
      },
      "score": 1,
      "content": "<meta>...<content># **Paper 1: A Study on LLM Scaling Laws**..."
    },
    {
      "metadata": {
        "file_name": "llm_paper_3.pdf",
        "source_url": "[https://arxiv.org/abs/2301.00003](https://arxiv.org/abs/2301.00003)",
        "tags": "LLM,RAG,NLP,knowledge,retrieval"
      },
      "score": 1,
      "content": "<meta>...<content># **Paper 3: Retrieval-Augmented Generation for NLP**..."
    }
  ]
}
```

**Response:**

```json
{
  "input_type": "json_body",
  "query": "What papers talk about RAG?",
  "summary": "Based on the provided summaries, the following paper discusses RAG: \n\n* **Paper 3: Retrieval-Augmented Generation for NLP**: This paper details the methodology, experiments, and results for RAG..."
}
```

-----

#### 2\. Summarize via File Upload

```http
POST /summarize/file/
```

This endpoint accepts a JSON file upload (`application/json` only) and an optional `query` as a form field.

**Headers:**

```
Authorization: Bearer your-secret-token-here
```

**Body (form-data):**

  - `file`: (file) `example_input.json`
  - `query`: (text) `What papers talk about RAG?`

**Response:**

```json
{
  "input_type": "file_upload",
  "filename": "example_input.json",
  "query": "What papers talk about RAG?",
  "summary": "Based on the provided summaries, the following paper discusses RAG: \n\n* **Paper 3: Retrieval-Augmented Generation for NLP**: This paper details the methodology, experiments, and results for RAG..."
}
```

## 🧪 Testing

### Using cURL

#### Test File Upload (`/summarize/file/`)

```bash
# Use example_input.json from the project
curl -X POST "[http://127.0.0.1:8000/summarize/file/](http://127.0.0.1:8000/summarize/file/)" \
 -H "Authorization: Bearer your-secret-token-here" \
 -F "file=@example_input.json" \
 -F "query=What papers talk about RAG?"
```

#### Test JSON Body (`/summarize/json/`)

*(Note: Assumes `example_input.json` is modified to include a "query" field)*

```bash
curl -X POST "[http://127.0.0.1:8000/summarize/json/](http://127.0.0.1:8000/summarize/json/)" \
 -H "Authorization: Bearer your-secret-token-here" \
 -H "Content-Type: application/json" \
 -d @example_input.json
```

### Using Swagger UI

Navigate to: `http://127.0.0.1:8000/docs`

1.  Click **"Authorize"** 🔒 (top right).
2.  Enter your token in the "Value" field: `your-secret-token-here`.
3.  Click **"Authorize"** and close the pop-up.
4.  You can now test the protected endpoints directly from the UI.

## 📁 Project Structure

```
LONG-DOCUMENT-SUMMARIZATION/
├── .env                     # Environment variables (BEARER_TOKEN, GOOGLE_API_KEY)
├── .gitattributes
├── .gitignore
├── api_server.py            # FastAPI server application
├── example_input.json       # Example input data for testing
├── main.py                  # Example standalone script (not part of the API server)
└── summarizer_service.py    # Core MapReduce and Gemini logic
```

## 🔒 Security

  - **Bearer Token Authentication:** All API endpoints are protected by the `verify_token` dependency, which checks for a valid `BEARER_TOKEN`.
  - **Environment Variables:** Sensitive keys (`GOOGLE_API_KEY`, `BEARER_TOKEN`) are loaded from `.env` and are not hardcoded.

<!-- end list -->

```
```
