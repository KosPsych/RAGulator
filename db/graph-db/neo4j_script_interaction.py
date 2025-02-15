import argparse
import logging
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)

# Use argparse and neo4j connection to run cypher query from command line
# argparse must have 2 arguments: mode  and query
# mode:
# - schema: get schema of the graph
# - query: run query

query = """
MATCH (p:person)-[e:directed]->(m:movie) WHERE m.name = 'The Godfather II'
RETURN p.name, e.year, m.name;
"""

parser = argparse.ArgumentParser(description='Run cypher query')
parser.add_argument('--mode', type=str, help='mode: schema or query')
parser.add_argument('--query', type=str, help='query to be executed')
args = parser.parse_args()

URI = "neo4j://localhost:7687"



 