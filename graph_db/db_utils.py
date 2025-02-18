from neo4j import GraphDatabase
import os
import time

def initialization():
    #time.sleep(5)
    # Connection details
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "neo4j"
    # Connect with default password and set the new password
    driver = GraphDatabase.driver(uri, auth=(username, password))
  
    with driver.session(database="system") as session:
                session.run(
                    "ALTER CURRENT USER SET PASSWORD FROM $old TO $new",
                    old="neo4j",
                    new=os.getenv('NEO4J_PASSWORD')
            )
    driver = GraphDatabase.driver(uri, auth=(username, os.getenv('NEO4J_PASSWORD')))
    with driver.session(database="neo4j") as session:
                session.run("CREATE FULLTEXT INDEX keyword_search IF NOT EXISTS FOR (n:Chunk) ON EACH [n.text]" )
                   

if __name__ == "__main__":
    initialization()


