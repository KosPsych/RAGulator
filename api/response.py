# response.py

import os
import json
import uuid
from datetime import datetime
import requests
from dotenv import load_dotenv
from openai_acess import OpenAIModel

load_dotenv()

class Response:
    def __init__(self):
        self.model = OpenAIModel()
        self.conversations = {}

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

    def rag_query_with_chunks(self, query: str, session_id: str, chunks_data: list):
        """
        Use the provided chunks (retrieved externally) along with the conversation history
        to build a prompt, then generate an answer via the model.
        
        Args:
            query: The user query or question.
            session_id: The conversation session ID.
            chunks_data: A list of chunk objects (or text) obtained from the Retrieval class.
        
        Returns:
            A tuple of (answer, sources).
        """

        conversation_history = self.format_history_for_prompt(session_id)

        chunks = []
        sources = []
        for item in chunks_data:
            chunk_text = item.get("text", "")
            chunks.append(chunk_text)
            sources.append(item)

        # 3) Build the "context" from chunk texts
        context = "\n\n".join(chunks)

        # 4) Build prompt
        prompt_message = f"""Based on the context provided below and the previous conversation,
please answer the following question. If the answer is not in the context, refer to the conversation
history or state that there is insufficient information.

Context:
{context}

Conversation History:
{conversation_history}

Question:
{query}
"""

        # 5) Send prompt to the model
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

        # Return final answer and the sources
        return result.get("response", ""), sources
