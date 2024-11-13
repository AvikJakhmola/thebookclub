from neo4j import GraphDatabase
from django.conf import settings  # Access Django settings

class Neo4jConnection:
    def __init__(self):
        # Create a driver instance for Neo4j Aura
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,  # The Aura DB URI
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)  # Username and password from settings
        )

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.data()
