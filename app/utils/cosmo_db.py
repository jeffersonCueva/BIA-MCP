from azure.cosmos import CosmosClient, PartitionKey
import os
from dotenv import load_dotenv

load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY", "").strip()

cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

def get_database(db_name: str):
    db_client = cosmos_client.get_database_client(db_name)
    return db_client

class CosmosContainer:
    def __init__(self, container_client):
        self.container = container_client

    async def find_one(self, query: dict):
        sql_query = "SELECT * FROM c WHERE " + " AND ".join(
            [f"c.{k} = '{v}'" for k, v in query.items()]
        )
        items = list(self.container.query_items(sql_query, enable_cross_partition_query=True))
        return items[0] if items else None

    async def find_all(self, query: dict):
        sql_query = "SELECT * FROM c WHERE " + " AND ".join(
            [f"c.{k} = '{v}'" for k, v in query.items()]
        )
        return list(self.container.query_items(sql_query, enable_cross_partition_query=True))

    async def update_one(self, query: dict, update: dict):
        item = await self.find_one(query)
        if not item:
            return None
        for k, v in update.items():
            item[k] = v
        return self.container.replace_item(item=item["id"], body=item)
