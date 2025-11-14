import google.generativeai as genai
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in the .env file")
genai.configure(api_key=API_KEY)


def group_chunks(chunks_content: List[str], batch_size: int = 7) -> List[str]:
    """
    Groups a list of text chunks into larger batches.

    Args:
        chunks_content: The list of individual text chunks.
        batch_size: The number of chunks to combine into a single batch.

    Returns:
        A new list where each item is a combined string of 'batch_size' chunks.
    """
    print(f"Grouping {len(chunks_content)} chunks into batches of {batch_size}...")
    grouped_text = []
    for i in range(0, len(chunks_content), batch_size):
        batch = chunks_content[i:i + batch_size]
        grouped_text.append("\n\n--- (New Chunk in Batch) ---\n\n".join(batch))
    print(f"Resulted in {len(grouped_text)} batches.")
    return grouped_text


async def summarize_batch_async(batch_content: str, index: int, query: Optional[str] = None) -> tuple[int, str]:
    """
    Summarizes a single BATCH of content, making it "query-aware".
    The function name is changed to reflect it's processing a batch.
    """
    print(f"Starting summarization for batch {index}...")
    try:
        if query:
            prompt = f"""
            This is a batch of content from a larger document. Summarize this specific batch while paying close attention 
            to any information that could help answer the following user question. 
            Extract all relevant details related to the question.
            IMPORTANT: The summary characters with spaces for this batch must not exceed 5000 characters.
            USER'S QUESTION: "{query}"

            --- CONTENT OF THIS BATCH ---
            {batch_content}
            --- QUERY-FOCUSED SUMMARY OF THIS BATCH ---
            """
        else:
            prompt = f"""
            This is a batch of content from a larger document. Summarize the key points from this batch concisely. 
            Focus on the main requirements, specifications, or objectives mentioned.
            IMPORTANT: The summary characters with spaces for this batch must not exceed 5000 characters.
            --- CONTENT ---
            {batch_content}
            --- GENERAL SUMMARY ---
            """

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async(prompt)
        print(f"Finished summarization for batch {index}")
        return (index, response.text.strip())
    except Exception as e:
        print(f"Error summarizing batch {index}: {e}")
        return (index, f"[Failed to summarize batch {index}]")


async def summarize_from_content_chunks(chunks_content: List[str], query: Optional[str] = None) -> str:
    """
    Orchestrates the query-aware MapReduce summarization process using batching.
    """
    batched_chunks = group_chunks(chunks_content, batch_size=7)

    print("Starting Map Phase: Creating query-aware tasks for each batch...")
    tasks = [asyncio.create_task(summarize_batch_async(batch, i + 1, query=query)) for i, batch in enumerate(batched_chunks)]
    
    map_results = await asyncio.gather(*tasks)
    
    map_results.sort(key=lambda x: x[0])
    individual_summaries = [result[1] for result in map_results]
    print("\nMap Phase complete.")
    print("\nStarting Reduce Phase...")
    combined_summaries = "\n\n---\n\n".join(individual_summaries)
    
    if query:
        print(f"Generating a final answer for the query: '{query}'")
        reduce_prompt = f"""
        Based on the following query-focused summaries, synthesize them into a single, coherent, and complete answer to the user's question.
        IMPORTANT: The summary characters with spaces for this batch must not exceed 5000 characters.
        USER'S QUESTION: "{query}"

        --- QUERY-FOCUSED SUMMARIES ---
        {combined_summaries}
        --- FINAL DETAILED ANSWER ---
        """
    else:
        print("Generating a general executive summary.")
        reduce_prompt = f"""
        From the following general summaries, compile a comprehensive and easy-to-understand executive summary.
        Cover key points like Project Overview, Objectives, Scope, Qualifications, Budget, and Timeline.
        Complete answer with markdown format and easy to read with bullet points.
        IMPORTANT: The summary characters with spaces for this batch must not exceed 5000 characters.

        --- GENERAL SUMMARIES ---
        {combined_summaries}
        --- FINAL EXECUTIVE SUMMARY ---
        """
    
    try:
        reduce_model = genai.GenerativeModel('gemini-2.5-flash')
        final_response = reduce_model.generate_content(reduce_prompt)
        print("Reduce Phase complete.")
        return final_response.text.strip()
    except Exception as e:
        return f"An error occurred during the Reduce phase: {e}"


async def summarize_from_file(file_path: str, query: Optional[str] = None) -> str:
    """
    Reads a JSON file and initiates the summarization process with an optional query.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        chunks_content = [item.get('content', '') for item in data.get('data', [])]
        if not chunks_content:
            return "No 'content' data found in the file."
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading or parsing the file: {e}"
    
    return await summarize_from_content_chunks(chunks_content, query=query)