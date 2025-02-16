# How to run

## 1. Create .env file to this folder

```
Azure OpenAI credentials (adjust variable names if required by your implementation)

AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_URL=https://your_azure_openai_url_here
AZURE_OPENAI_MODEL_NAME=your_model_name_here
AZURE_OPENAI_API_VERSION=your_api_version_here

# API endpoints for the RAG system
EMBEDDING_URL=https://embeddingmodel-emgsc9drgwefg0ea.francecentral-01.azurewebsites.net/embed
GET_CHUNKS_URL=https://codequestai-hnbxb5d2hfgnegav.francecentral-01.azurewebsites.net/get_chunks
```
2. Run the main script:

```python main.py```