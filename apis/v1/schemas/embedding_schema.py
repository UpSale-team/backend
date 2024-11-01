from typing import List, AnyStr, Dict
import uuid
import numpy as np
from fastapi import HTTPException, status
from ..providers import word_embedding_provider, vector_db
from ..utils.constants import DEFAULT_EMBEDDING_PROVIDER, DEFAULT_QUERY_LIMIT


class VectorEmbeddingSchema:
    def __init__(
        self,
        ids: List[AnyStr],
        vectors: List[List[float]],
        documents: List[AnyStr],
        payloads: List[Dict],
        provider: AnyStr = DEFAULT_EMBEDDING_PROVIDER,
    ):
        self.ids = ids
        self.vectors = [np.array(vector) for vector in vectors]
        self.documents = documents
        self.payloads = payloads
        self.provider = provider

    def __iter__(self):
        return zip(self.ids, self.vectors, self.documents, self.payloads)

    @staticmethod
    def from_documents(documents: List[AnyStr], payloads: List[Dict], provider: AnyStr = DEFAULT_EMBEDDING_PROVIDER):
        vectors = word_embedding_provider.embed(documents, provider)
        # Tạo ID ngẫu nhiên cho từng vector
        ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        return VectorEmbeddingSchema(ids, vectors, documents, payloads, provider)

    @staticmethod
    def from_database(collection: AnyStr):
        records = vector_db.get_all(collection)
        ids = []
        vectors = []
        documents = []
        payloads = []
        for record in records:
            ids.append(record.id)
            vectors.append(record.vector)
            documents.append(record.payload["document"])
            payloads.append(record.payload["payload"])
        return VectorEmbeddingSchema(ids, vectors, documents, payloads)

    @staticmethod
    def from_query(collection: AnyStr, key: AnyStr, value: AnyStr):
        records = vector_db.dynamic_search(collection, key, value)
        ids = []
        vectors = []
        documents = []
        payloads = []
        for record in records:
            ids.append(record.id)
            vectors.append(record.vector)
            documents.append(record.payload["document"])
            payloads.append(record.payload["payload"])
        return VectorEmbeddingSchema(ids, vectors, documents, payloads)

    def upload(self, collection: AnyStr):
        try:
            vector_db.upload_documents_and_load_collection(self.documents, self.vectors, self.payloads, collection)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to upload vectors: {str(e)}"
            )

    def search(
        self,
        collection: AnyStr,
        limit: int = DEFAULT_QUERY_LIMIT,
    ):
        try:
            return vector_db.search(collection, self.vectors, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to search vectors: {str(e)}"
            )

    def delete(self, collection: AnyStr):
        try:
            vector_db.delete(collection, self.ids)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to delete vectors: {str(e)}"
            )

    def get_retriever(self):
        """Trả về một retriever để tìm kiếm trong cơ sở dữ liệu."""
        return vector_db.get_retriever()
