from flask import Flask, request, jsonify
import os
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer(os.environ.get('MODEL_PATH'))

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    if request.method == 'GET':
        texts = request.args.getlist("text")

        if texts:
            embeddings = model.encode(texts).tolist()
            return jsonify(embeddings)

        return 'No text provided', 400
    if request.method == 'POST':
        data = request.get_json()['text']
        if data:
            embeddings = model.encode(data).tolist()
            return jsonify(embeddings)
