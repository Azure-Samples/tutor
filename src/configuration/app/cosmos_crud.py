import os
from typing import List, Optional, AsyncIterator

from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from azure.identity.aio import DefaultAzureCredential


class CosmosCRUD:
    def __init__(self, container_env_var: str):
        self.cosmos_endpoint = os.getenv("COSMOS_ENDPOINT", "")
        self.database_name = os.getenv("COSMOS_QNA_NAME", "")
        self.container_name = os.getenv(container_env_var, "")
        print(f"Container name: {self.container_name}")
        print(f"Cosmos endpoint: {self.cosmos_endpoint}")
        if not self.cosmos_endpoint or not self.database_name or not self.container_name:
            raise ValueError("Missing required environment variables for CosmosDB configuration.")

    async def _get_container(self) -> AsyncIterator:
        """
        Gerencia o contexto do CosmosClient e retorna o container.
        """
        client = CosmosClient(self.cosmos_endpoint, DefaultAzureCredential())
        async with client:
            try:
                database = client.get_database_client(self.database_name)
                await database.read()
            except exceptions.CosmosResourceNotFoundError:
                await client.create_database(self.database_name)
                database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            yield container

    async def list_items(self, query: str = "SELECT * FROM c", parameters: Optional[List] = None) -> list:
        """
        List items in the container using a SQL query.
        """
        if parameters is None:
            parameters = []
        async for container in self._get_container():
            items = [item async for item in container.query_items(query=query, parameters=parameters)]
            return items
        return []

    async def create_item(self, item: dict):
        """
        Create or upsert an item in the container.
        """
        async for container in self._get_container():
            response = await container.upsert_item(item)
            return response
        return None

    async def read_item(self, item_id: str, partition_key_value: Optional[str] = None):
        """
        Read an item by id and partition key value (defaults to item_id).
        """
        pk = partition_key_value if partition_key_value is not None else item_id
        async for container in self._get_container():
            response = await container.read_item(item=item_id, partition_key=pk)
            return response
        return None

    async def update_item(self, item_id: str, item: dict, partition_key_value: Optional[str] = None):
        """
        Replace an item by id and partition key value (defaults to item_id).
        The item dict must include the id and partition key fields.
        """
        pk = partition_key_value if partition_key_value is not None else item_id
        async for container in self._get_container():
            response = await container.replace_item(item=item_id, body=item, partition_key=pk)
            return response
        return None

    async def delete_item(self, item_id: str, partition_key_value: Optional[str] = None):
        """
        Delete an item by id and partition key value (defaults to item_id).
        """
        pk = partition_key_value if partition_key_value is not None else item_id
        async for container in self._get_container():
            response = await container.delete_item(item=item_id, partition_key=pk)
            return response
        return None
