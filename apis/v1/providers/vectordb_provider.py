from typing import AnyStr, Dict, Any, List, Union
from langchain_qdrant import Qdrant
from qdrant_client.http.models import (
    models,
    VectorParams,
    Distance,
)
import os
from ..utils.constants import DEFAULT_EMBEDDING_PROVIDER, DEFAULT_EMBEDDING_DIM
from ..configs.qdrant_config import qdrant_client
from ..configs.word_embedding_config import hgf_embedder
from ..utils.logger import logger_decorator

class VectorDatabaseProvider:
    def __init__(self, collection_name):
        self.qdrant = None
        self.collection_name = collection_name

    @logger_decorator(prefix="VECTOR_DATABASE")
    def create_collection(
        self,
        provider: AnyStr = DEFAULT_EMBEDDING_PROVIDER,
        size: int = DEFAULT_EMBEDDING_DIM,
        distance: Distance = Distance.COSINE
    ):
        if not qdrant_client.collection_exists(collection_name=self.collection_name):
            qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=size, distance=distance),
            )
        return True

    @logger_decorator(prefix="VECTOR_DATABASE")
    def delete_collection(self):
        try:
            qdrant_client.delete_collection(collection_name=self.collection_name)
            return True
        except Exception as e:
            print(f"Exception: {e}")
            return False

    @logger_decorator(prefix="VECTOR_DATABASE")
    def upload_documents_and_load_collection(self, splits):
        qdrant = Qdrant.from_documents(
            documents=splits, 
            embedding=embedder, 
            url=qdrant_client.host, 
            api_key=qdrant_client.api_key, 
            prefer_grpc=True, 
            collection_name=self.collection_name
        )
        self.qdrant = qdrant
        return qdrant

    @logger_decorator(prefix="VECTOR_DATABASE")
    def load_collection(self):
        qdrant = Qdrant.from_existing_collection(
            embedding=embedder,
            url=qdrant_client.host, 
            api_key=qdrant_client.api_key,
            prefer_grpc=True, 
            collection_name=self.collection_name
        )
        self.qdrant = qdrant
        return qdrant

    @logger_decorator(prefix="VECTOR_DATABASE")
    def get_retriever(self):
        retriever = self.qdrant.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        return retriever
