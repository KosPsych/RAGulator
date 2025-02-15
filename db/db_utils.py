from neo4j import GraphDatabase
import os
import time

def change_password():
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
  


if __name__ == "__main__":
    change_password()


