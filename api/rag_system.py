import os
import json
import uuid
from datetime import datetime
import requests
from openai_acess import OpenAIModel

conversations = {}

def create_session():
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    conversations[session_id] = []
    return session_id

def add_message(session_id: str, role: str, content: str):
    """Add a message to the conversation history."""
    if session_id not in conversations:
        conversations[session_id] = []
    conversations[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

def get_conversation_history(session_id: str, max_messages: int = None):
    """Retrieve the conversation history for a session."""
    history = conversations.get(session_id, [])
    return history[-max_messages:] if max_messages else history

def format_history_for_prompt(session_id: str, max_messages: int = 5):
    """Format conversation history for inclusion in prompts."""
    history = get_conversation_history(session_id, max_messages)
    formatted = ""
    for msg in history:
        role = "Human" if msg["role"] == "user" else "Assistant"
        formatted += f"{role}: {msg['content']}\n\n"
    return formatted.strip()

def get_embedding(text: str):
    """
    Send a request to the deployed embedding model to get the embedding.
    The endpoint expects a payload in the form: {'text': ['your text']}
    """
    url = "https://embeddingmodel-emgsc9drgwefg0ea.francecentral-01.azurewebsites.net/embed"
    payload = {"text": [text]}
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    result = response.json()
    print (result)
    if result is None:
        raise ValueError("No embedding returned from the deployed model.")

    if result is None:
        raise ValueError("No embedding found in the response.")
    return result

def get_chunks_from_api(query_string):
    """

    """
    api_url = "https://codequestai-hnbxb5d2hfgnegav.francecentral-01.azurewebsites.net/get_chunks"
    headers = {'Content-Type': 'application/json'}
    payload = {'query_string': query_string}

    try:
        response = requests.get(api_url, headers=headers, json=payload)
        response.raise_for_status() 
        return response.json()       
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

def retrieve_chunks_from_endpoint(query: str, top_k: int = 5):
    """
    Retrieves the top_k most relevant document chunks based on the user query.
    It computes the query embedding, builds a Cypher query that scores each document by cosine similarity,
    and then sends the query to the Neo4j API endpoint.

    Args:
        query (str): The user query.
        top_k (int, optional): The number of top results to return. Defaults to 5.

    Returns:
        A list of document chunks (e.g. tuples containing text and page).
    """
    query_embedding = get_embedding(query)

    cypher_query = f"""
    MATCH (n:Chunk)
    WITH n, gds.similarity.cosine(n.embedding, {query_embedding}) AS similarity
    RETURN n.text AS text, n.page AS page
    ORDER BY similarity DESC
    LIMIT {top_k}
    """
    
    return get_chunks_from_api(cypher_query)


def rag_query(query: str, session_id: str, n_chunks: int = 3):
    """
    Retrieve relevant chunks from the DB via the endpoint, build a prompt using conversation history,
    and generate an answer using the OpenAIModel's predict method.
    """
    conversation_history = format_history_for_prompt(session_id)
    
    chunks, sources = retrieve_chunks_from_endpoint(query, top_k=n_chunks)
    
    context = "\n\n".join(chunks)
    
    prompt_message = f"""Based on the context provided below and the previous conversation,
please answer the following question. If the answer is not in the context, refer to the conversation
history or state that there is insufficient information.

Context:
{context}

Conversation History:
{conversation_history}

Question:
{query}"""
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
        {"role": "user", "content": prompt_message}
    ]
    
    params = {
        "temperature": 0.0,
        "max_tokens": 500
    }
    
    inputs = {"messages": messages, "params": params}
    
    model = OpenAIModel()
    result = model.predict(inputs)
    
    add_message(session_id, "user", query)
    add_message(session_id, "assistant", result.get("response", ""))
    
    return result.get("response", ""), sources

if __name__ == "__main__":
    session_id = create_session()
    
    query = "When was GreenGrow Innovations founded?"
    
    answer, used_sources = rag_query(query, session_id)
    
    print("Answer:", answer)
    print("Sources:", used_sources)
