from flask import Flask, jsonify, request
from neo4j import GraphDatabase
import os
app = Flask(__name__)
import time
import ast
import json


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
    driver = GraphDatabase.driver(uri, auth=(username, password))
    # Establish connection
    try:
        
        with driver.session() as session:
            result = session.run("RETURN 'Connection Successful' AS message")
            for record in result:
                print(record["message"])
        return(jsonify("Connected to Neo4j successfully!"))
    except Exception as e:
        return(jsonify(f"Connection failed: {e}"))
      
    finally:
        driver.close()

@app.route('/get_chunks', methods=['GET'])
def get_items():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    

    
    embedding =input_data['embedding']
    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
    chunk_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        result =  inner_session.run(input_data['query_string'], embedding=embedding)

        for r in result:
           chunk_list.append( (r['text'], r['page'], r['name'], r['base64'], r['score']))  
    return jsonify(chunk_list)


@app.route('/get_documents', methods=['GET'])
def get_documents():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])
    
    
    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
    document_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        result =  inner_session.run(input_data['query_string'])

        for r in result:
           document_list.append( (r['name'], r['language'], r['tag']))

    return jsonify(document_list)


@app.route('/keyword_search', methods=['GET'])
def keyword_search():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])
 
    params = {'query': input_data['query']}
    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
    chunk_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        result = inner_session.run(input_data['query_string'], params)
        for r in result:
           chunk_list.append( (r['text'], r['page'], r['name'], r['base64'], r['score']))

    return jsonify(chunk_list)


@app.route('/arbitrary_query', methods=['POST'])
def arbitrary_query():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])
  
    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
   
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        inner_session.run(input_data['query_string'])

    return jsonify('done')


@app.route('/add_chunk', methods=['POST'])
def add_chunk():
    # Get the JSON data sent in the request body
    input_data = request.get_json()   

    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = os.getenv('NEO4J_PASSWORD')
    driver = GraphDatabase.driver(uri, auth=(username, password))
    if 'embedding' in input_data:
        embedding = input_data['embedding']
        with driver.session() as inner_session:
            inner_session.run(input_data['query_string'], embedding=embedding)
    else:
        with driver.session() as inner_session:
            inner_session.run(input_data['query_string'])

    return jsonify('done')


