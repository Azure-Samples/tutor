"""Shared Cosmos client helpers."""

from __future__ import annotations

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential


def create_cosmos_client(endpoint: str) -> tuple[DefaultAzureCredential, CosmosClient]:
    credential = DefaultAzureCredential()
    client = CosmosClient(endpoint, credential=credential)
    return credential, client
