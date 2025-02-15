from flask import Flask, jsonify, request
from neo4j import GraphDatabase
app = Flask(__name__)



@app.route('/healthcheck', methods=['GET'])
def healthcheck():

    # Connection details
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "12345678"

    # Establish connection
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
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
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])
    

    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = '12345678' 
    chunk_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        result =  inner_session.run(input_data['query_string'])

        for r in result:
           chunk_list.append( (r['text'], r['page']))

    return jsonify(chunk_list)


@app.route('/add_document', methods=['POST'])
def add_document():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])

    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = '12345678' 
    chunk_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        nner_session.run(input_data['query_string'])

    return jsonify('done')


@app.route('/add_chunk', methods=['POST'])
def add_chunk():
    # Get the JSON data sent in the request body
    input_data = request.get_json()
    
    # Print the received input data
    print("Query_string:", input_data['query_string'])
    

    # Connect to Neo4j
    uri = "neo4j://localhost:7687"
    username = 'neo4j'
    password = '12345678' 
    chunk_list = []
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as inner_session:
        nner_session.run(input_data['query_string'])

    return jsonify('done')


