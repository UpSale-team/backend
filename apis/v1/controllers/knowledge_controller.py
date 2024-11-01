from typing import AnyStr, List
from fastapi import HTTPException, status, UploadFile, BackgroundTasks
import uuid
import time
from ..schemas.user_schema import UserSchema
from ..schemas.knowledge_schema import KnowledgeSchema
from ..schemas.embedding_schema import VectorEmbeddingSchema
from ..providers import memory_cacher, storage_db
from ..utils.utils import get_content_type, validate_file_extension
from ..utils.extractor import get_document_content


def _validate_permissions(user: UserSchema):
    # Kiểm tra nếu người dùng đã đăng nhập hoặc có quyền truy cập
    if user is None:  # Kiểm tra xem người dùng có tồn tại không
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource."
        )
    
    return True  # Nếu người dùng có quyền truy cập, trả về True

def get_all_knowledges(user: UserSchema):
    _validate_permissions(user)

    # Get Knowledge
    knowledges = KnowledgeSchema.find_all()  # Lấy tất cả kiến thức
    return knowledges

def _upload_knowledge_data(data: bytes, filename: AnyStr, watch_id: AnyStr, knowledge: KnowledgeSchema):
    # Get content type of file
    content_type = get_content_type(filename)
    path, url = storage_db.upload(data, filename, content_type)
    memory_cacher.get(watch_id)["percent"][filename] += 15
    knowledge.update_path_url(path, url)
    memory_cacher.get(watch_id)["percent"][filename] += 5


def _upload_multiple_knowledge(knowledges: List[bytes], filenames: List[AnyStr], watch_id: AnyStr):
    for knowledge, filename in zip(knowledges, filenames):
        memory_cacher.get(watch_id)["percent"][filename] = 0

        # Create Knowledge document in database
        knowledge_instance = KnowledgeSchema(name=filename).create_knowledge()
        memory_cacher.get(watch_id)["percent"][filename] += 10

        # Upload to storage
        try:
            _upload_knowledge_data(knowledge, filename, watch_id, knowledge_instance)
        except Exception as e:
            memory_cacher.get(watch_id)["error"][filename] = str(e)
            continue

        # Save file to cache folder
        cache_file_path = memory_cacher.save_cache_file(knowledge, filename)
        knowledge_content = get_document_content(cache_file_path)
        memory_cacher.remove_cache_file(filename)
        memory_cacher.get(watch_id)["percent"][filename] += 5

        # Update content
        knowledge_instance.update_content(knowledge_content)
        memory_cacher.get(watch_id)["percent"][filename] += 5

    # Wait for 10 seconds to remove watch id
    time.sleep(10)
    memory_cacher.remove(watch_id)

def _upload_single_knowledge(knowledge: bytes, filename: AnyStr, watch_id: AnyStr):
    memory_cacher.get(watch_id)["percent"][filename] = 0

    # Create Knowledge document in database
    knowledge_instance = KnowledgeSchema(name=filename).create_knowledge()  # Sửa lại đây
    memory_cacher.get(watch_id)["percent"][filename] += 10

    # Upload to storage
    try:
        _upload_knowledge_data(knowledge, filename, watch_id, knowledge_instance)
    except Exception as e:
        memory_cacher.get(watch_id)["error"][filename] = str(e)
        return

    # Save file to cache folder
    cache_file_path = memory_cacher.save_cache_file(knowledge, filename)
    knowledge_content = get_document_content(cache_file_path)
    memory_cacher.remove_cache_file(filename)
    memory_cacher.get(watch_id)["percent"][filename] += 5

    # Update content
    knowledge_instance.update_content(knowledge_content)
    memory_cacher.get(watch_id)["percent"][filename] += 5

    # Wait for 10 seconds to remove watch id
    time.sleep(10)
    memory_cacher.remove(watch_id)

async def upload_knowledges_data(user: UserSchema, knowledges: List[UploadFile], bg_tasks: BackgroundTasks):
    # Validate permission
    _validate_permissions(user)

    # Create watch id
    watch_id = str(uuid.uuid4())

    # Read files
    files: List[bytes] = []
    filenames: List[AnyStr] = []
    for knowledge in knowledges:
        file_content = await knowledge.read()
        files.append(file_content)
        filenames.append(knowledge.filename)

    # Initialize cache
    memory_cacher.set(watch_id, {
        "percent": {},
        "error": {}
    })

    # Upload knowledges
    bg_tasks.add_task(_upload_multiple_knowledge, files, filenames, watch_id)

    return watch_id

async def upload_knowledge_data(user: UserSchema, knowledge: UploadFile, bg_tasks: BackgroundTasks):
    # Validate extension
    validate_file_extension(knowledge.filename)

    # Validate permission
    _validate_permissions(user)

    # Read file
    file_content = await knowledge.read()

    # Create watch id
    watch_id = str(uuid.uuid4())

    # Initialize cache
    memory_cacher.set(watch_id, {
        "percent": {},
        "error": {}
    })

    # Upload knowledge
    bg_tasks.add_task(_upload_single_knowledge, file_content, knowledge.filename, watch_id)

    return watch_id

def get_upload_progress(watch_id: AnyStr):
    return memory_cacher.get(watch_id)

async def download_knowledge_content(knowledge_id: AnyStr, user: UserSchema) -> bytes:
    # Validate permission
    _validate_permissions(user)

    # Get Knowledge
    knowledge = KnowledgeSchema.find_by_id(knowledge_id)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge not found."
        )

    knowledge_content = knowledge.download_content()
    if not knowledge_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge content not found."
        )

    return knowledge_content

def delete_knowledges_by_ids(knowledge_ids: List[AnyStr]):
    for knowledge_id in knowledge_ids:
        knowledge = KnowledgeSchema.find_by_id(knowledge_id)
        if knowledge:
            knowledge.delete_knowledge()

def delete_current_knowledge(knowledge_id: AnyStr, user: UserSchema):
    # Validate permission
    _validate_permissions(user)

    # Get Knowledge
    knowledge = KnowledgeSchema.find_by_id(knowledge_id)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge not found."
        )

    # Delete vectors
    VectorEmbeddingSchema.from_query(
        collection="project_collection",  # Cần thay đổi nếu cần
        key="id",
        value=knowledge_id
    ).delete("project_collection")  # Cần thay đổi nếu cần

    # Delete Knowledge
    knowledge.delete_knowledge()

def get_retriever(knowledge_id: AnyStr, user: UserSchema):
    # Validate permission
    _validate_permissions(user)

    # Get Knowledge
    knowledge = KnowledgeSchema.find_by_id(knowledge_id)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge not found."
        )

    return VectorEmbeddingSchema.from_query(
        collection="project_collection",  # Cần thay đổi nếu cần
        key="id",
        value=knowledge_id
    ).get_retriever()
