import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from response import Response

# Load environment variables from .env
load_dotenv()

# Retrieve environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
EMBEDDING_URL = os.getenv("EMBEDDING_URL")
GET_CHUNKS_URL = os.getenv("GET_CHUNKS_URL")


from intent_recognition import IntentRecognizer
from retrieval import Retrieval


app = FastAPI()


intent_recognizer = IntentRecognizer()
response = Response()

class GenerateResponseInput(BaseModel):
    query: str
    top_k: Optional[int] = 5  

@app.post("/generate_response")
def generate_response(data: GenerateResponseInput):
    """
    1) Classify & translate the user's query.
    2) Retrieve relevant document chunks (via Retrieval).
    3) Pass everything to the RAG system (Response) to generate a final answer.
    4) Return final answer + sources.
    """

    classification_result = intent_recognizer.classify_and_translate(data.query)
    category = classification_result["category"]
    translation = classification_result["translation"]
    language = classification_result["language"] 

    if language == "english":
        english_query = data.query
        greek_query = translation
    elif language == "greek":
        english_query = translation
        greek_query = data.query
    else:
        english_query = data.query
        greek_query = "unknown"

    retrieval_instance = Retrieval(
        top_k=data.top_k,
        english_query=english_query,
        greek_query=greek_query,
        category=category,
        embedding_url=EMBEDDING_URL,
        db_url=GET_CHUNKS_URL
    )

    try:
        retrieved_results = retrieval_instance.retrieve()
    except Exception as e:
        return {
            "error": str(e),
            "category": category,
        }

    session_id = response.create_session()
    final_answer, used_sources = response.rag_query_with_chunks(
        query=data.query,
        session_id=session_id,
        chunks_data=retrieved_results   
    )

    return {
        "category": category,
        "final_answer": final_answer,
        "used_sources": used_sources
    }
