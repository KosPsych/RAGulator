from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Constants to use throughout the application (e.g. database URL, top-k results to return, etc.)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
EMBEDDING_URL = os.getenv("EMBEDDING_URL")
DB_URL = os.getenv("DB_URL")