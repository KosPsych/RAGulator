import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import List, Dict, Generator

# Load environment variables
if os.getcwd() != '/app':
    load_dotenv()

# Get Azure OpenAI credentials from environment variables
azure_endpoint = os.getenv("OPENAI_API_URL")
azure_api_key = os.getenv("OPENAI_API_KEY")
model_deployment_name = os.getenv("OPENAI_MODEL_NAME")
api_version = os.getenv("OPENAI_API_VERSION")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=azure_api_key,
    api_version=api_version
)

def get_azure_openai_response_stream(system_prompt, user_prompt: str, chat_history: List[Dict[str, str]] = None) -> Generator[str, None, None]:
    """
    Get streaming response from Azure OpenAI.
    
    Args:
        query (str): The user's current query
        chat_history (List[Dict]): List of previous queries and responses
        
    Returns:
        Generator: A generator that yields chunks of the response as they come in
    """
    try:
        # Prepare messages for the API call
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        
        # Add chat history for context if available
        # if chat_history:
        #     # Convert chat history to the format expected by OpenAI
        #     for chat in chat_history[-3:]:  # Use last 3 exchanges for context
        #         messages.insert(0, {"role": "user", "content": chat["query"]})
        #         messages.insert(1, {"role": "assistant", "content": chat["response"]})
        
        # Call Azure OpenAI API with streaming enabled
        response = client.chat.completions.create(
            model=model_deployment_name,
            messages=messages,
            temperature=0,
            stream=True  # Enable streaming
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
    
    except Exception as e:
        error_message = f"Error getting response from Azure OpenAI: {str(e)}"
        print(error_message)  # Log to console
        yield f"I'm sorry, I encountered an error: {str(e)}"