import requests

def get_embedding(text: str):
    """
    Sends a POST request to the deployed embedding model endpoint
    and returns the embedding for the given text.

    The endpoint expects a payload of the form:
        {'text': ['your text']}
    """
    url = "https://embeddingmodel-emgsc9drgwefg0ea.francecentral-01.azurewebsites.net/embed"
    payload = {"text": [text]}
    
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raises an error if the request fails
    
    result = response.json()
    
    if result is None:
        raise ValueError("No embedding returned from the deployed model.")
    
    return result

if __name__ == "__main__":
    # Example text to test the embedding model
    text_to_embed = "This is a test sentence to generate an embedding."
    embedding = get_embedding(text_to_embed)
    
    print("Input text:", text_to_embed)
    print("Embedding:", embedding)
