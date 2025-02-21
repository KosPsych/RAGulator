import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv

from reranking import rerank
from utils.constants import *
from rephrase import rephrase



from intent_recognition import IntentRecognizer
from retrieval import Retrieval


app = FastAPI()


intent_recognizer = IntentRecognizer()

class GenerateResponseInput(BaseModel):
    query: str
    top_k: Optional[int] = 5 ,
    chat_history: List[Dict[str, str]] = []

@app.post("/generate_response")
def generate_response(data: GenerateResponseInput):
    """
    1) Classify & translate the user's query.
    2) Retrieve relevant document chunks (via Retrieval).
    3) Pass everything to the RAG system (Response) to generate a final answer.
    4) Return final answer + sources.
    """
    print("="*100)
    print(data.query)
    print("="*100)
    chat_history = data.chat_history
    rephrased_query = rephrase(chat_history, data.query)
  
    classification_result = intent_recognizer.classify_and_translate(rephrased_query)
    category = classification_result["category"]
    translation = classification_result["translation"]
    language = classification_result["language"] 

    if language == "english":
        english_query = rephrased_query
        greek_query = translation
    elif language == "greek":
        english_query = translation
        greek_query = rephrased_query
    else:
        english_query = rephrased_query
        greek_query = "unknown"
    
    retrieval_instance = Retrieval(
        top_k=data.top_k,
        english_query=english_query,
        greek_query=greek_query,
        category=category,
        embedding_url=EMBEDDING_URL,
        db_url=DB_URL
    )

    try:
        retrieved_results = retrieval_instance.retrieve()
    except Exception as e:
        return {
            "error": str(e),
            "category": category,
        }
    
    reranked_results = rerank(retrieved_results)
    return reranked_results
