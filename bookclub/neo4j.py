from django.conf import settings
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri=None, user=None, password=None):
        # Use parameters if provided; otherwise, fall back to settings
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USERNAME
        self.password = password or settings.NEO4J_PASSWORD
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.data()
