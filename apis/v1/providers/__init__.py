from .memory_provider import MemoryProvider
# from .word_embedding_provider import WordEmbeddingProvider
from .vectordb_provider import VectorDatabaseProvider
from .storage_provider import StorageProvider
from .db_provider import DatabaseProvider
from .jwt_provider import JWTProvider
from ..utils.constants import (
USER_COLLECTION,
KNOWLEDGE_STORAGE,
KNOWLEDGE_COLLECTION,
PROJECT_COLLECTION
)



# Define Providers
memory_cacher = MemoryProvider()
jwt = JWTProvider()
user_db = DatabaseProvider(collection_name=USER_COLLECTION)
project_db = DatabaseProvider(collection_name=PROJECT_COLLECTION)
knowledge_db = DatabaseProvider(collection_name=KNOWLEDGE_COLLECTION)
storage_db = StorageProvider(directory=KNOWLEDGE_STORAGE)
vector_db = VectorDatabaseProvider(collection_name="KNOWLEDGE")
