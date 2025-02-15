import os
from dotenv import load_dotenv
from openai_acess import OpenAIModel  # Ensure this matches the file name where OpenAIModel is defined

load_dotenv()

model = OpenAIModel()

inputs = {
    'messages': [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    'params': {
        'temperature': 0.7,
        'max_tokens': 100
    }
}

response = model.predict(inputs)

print("Model Response:", response["response"])
