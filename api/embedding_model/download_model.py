import sentence_transformers
import os
from sentence_transformers import SentenceTransformer

os.environ['CURL_CA_BUNDLE'] = ''

st_model = SentenceTransformer("avsolatorio/GIST-Embedding-v0")
model_dir = os.environ.get('MODEL_PATH')
st_model.save(model_dir)