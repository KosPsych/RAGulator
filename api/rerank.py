

class Rerank():
    def __init__(self):
        self.rerank = True
    

    def rerank(self):
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