import os
import json
import uuid
from datetime import datetime
import requests
from dotenv import load_dotenv
from openai_acess import OpenAIModel

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.model = OpenAIModel()
        self.conversations = {}
        self.embedding_url = os.getenv("EMBEDDING_URL")
        if not self.embedding_url:
            raise ValueError("Missing EMBEDDING_URL environment variable.")
        self.get_chunks_url = os.getenv("GET_CHUNKS_URL")
        if not self.get_chunks_url:
            raise ValueError("Missing GET_CHUNKS_URL environment variable.")

    def create_session(self) -> str:
        """Create a new conversation session and return its session ID."""
        session_id = str(uuid.uuid4())
        self.conversations[session_id] = []
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_history(self, session_id: str, max_messages: int = None):
        """Retrieve the conversation history for a session."""
        history = self.conversations.get(session_id, [])
        return history[-max_messages:] if max_messages else history

    def format_history_for_prompt(self, session_id: str, max_messages: int = 5) -> str:
        """Format conversation history for inclusion in prompts."""
        history = self.get_conversation_history(session_id, max_messages)
        formatted = ""
        for msg in history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n\n"
        return formatted.strip()

    def get_embedding(self, text: str):
        """
        Get an embedding for the provided text by calling the deployed embedding model.
        """
        payload = {"text": [text]}
        response = requests.post(self.embedding_url, json=payload)
        response.raise_for_status()
        result = response.json()
        if result is None:
            raise ValueError("No embedding returned from the deployed model.")
        return result

    def get_chunks_from_api(self, query_string: str, query_embedding: list):
        """
        Send a request to retrieve document chunks based on the Cypher query.
        """
        headers = {'Content-Type': 'application/json'}
        payload = {'query_string': query_string,
                   'embedding': query_embedding}
        # print ("QUERY STRING", query_string)
        # print ("QUERY eMB", query_embedding)
        # print ("QUERY PAY", payload)
        try:
            response = requests.get(self.get_chunks_url, headers=headers, json=payload)
            response.raise_for_status()
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def retrieve_chunks_from_endpoint(self, query: str, top_k: int = 5):
        """
        Retrieve the top_k most relevant document chunks based on the user query.
        Computes the query embedding, builds a Cypher query for Neo4j, and returns the result.
        """
        query_embedding = self.get_embedding(query)
        cypher_query = f"""
        MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
        WITH c, gds.similarity.cosine(c.embedding, $embedding) AS score
        ORDER BY score DESC
        WITH DISTINCT c, score
        RETURN c.text AS text, c.page AS page
        LIMIT {top_k}
        """
        return self.get_chunks_from_api(cypher_query, query_embedding[0])

    def rag_query(self, query: str, session_id: str, n_chunks: int = 5):
        """
        Retrieve relevant document chunks, build a prompt using conversation history,
        and generate an answer using the OpenAI model.
        """
        conversation_history = self.format_history_for_prompt(session_id)
        chunks_data = self.retrieve_chunks_from_endpoint(query, top_k=n_chunks)
        print(chunks_data)
        # Process the chunks data.
        chunks = []
        sources = []
        if chunks_data:
            for item in chunks_data:
                chunks.append(item[0])
                sources.append(item[0])
        context = "".join(chunk for chunk in chunks)
        

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

        result = self.model.predict(inputs)
        self.add_message(session_id, "user", query)
        self.add_message(session_id, "assistant", result.get("response", ""))
        print(prompt_message)
        return result.get("response", ""), sources


if __name__ == "__main__":
    rag_system = RAGSystem()
    session_id = rag_system.create_session()
    query = "When was GreenGrow Innovations founded?"
    answer, used_sources = rag_system.rag_query(query, session_id)
    print("Answer:", answer)
    print("Sources:", used_sources)
