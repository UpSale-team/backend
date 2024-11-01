from typing import Annotated, List
from io import BytesIO
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile
from fastapi.responses import StreamingResponse
from ..schemas.user_schema import UserSchema
from ..middlewares.auth_middleware import get_current_user
from ..controllers.knowledge_controller import (
    get_all_knowledges,
    upload_knowledge_data, 
    upload_knowledges_data,
    download_knowledge_content,
    delete_current_knowledge,
)
from ..schemas.knowledge_schema import KnowledgeSchema
from ..utils.response_fmt import jsonResponseFmt

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.get("/")
async def list_knowledge(user: Annotated[UserSchema, Depends(get_current_user)]):
    knowledge_docs = get_all_knowledges(user)  # Truyền user vào hàm
    return jsonResponseFmt([doc.to_dict() for doc in knowledge_docs])

@router.get("/{knowledge_id}")
async def get_knowledge(knowledge_id: str, user: Annotated[UserSchema, Depends(get_current_user)]):
    knowledge_doc = KnowledgeSchema.find_by_id(knowledge_id)  # Sử dụng phương thức tìm kiếm của KnowledgeSchema
    if not knowledge_doc:
        return jsonResponseFmt(None, "Knowledge not found", status_code=404)
    return jsonResponseFmt(knowledge_doc.to_dict())

@router.post("/uploads/single")
async def upload_single_knowledge_api(
    user: Annotated[UserSchema, Depends(get_current_user)],
    file: UploadFile,
    bg_tasks: BackgroundTasks,
):
    watch_id = await upload_knowledge_data(user, file, bg_tasks)
    return jsonResponseFmt({"filename": file.filename, "status": "Uploaded successfully", "watch_id": watch_id})

@router.post("/uploads/multiple")
async def upload_multiple_knowledge_api(
    user: Annotated[UserSchema, Depends(get_current_user)],
    files: List[UploadFile],
    bg_tasks: BackgroundTasks,
):
    watch_id = await upload_knowledges_data(user, files, bg_tasks)
    return jsonResponseFmt({"status": "All files uploaded successfully", "watch_id": watch_id})

@router.get("/{knowledge_id}/download", response_class=StreamingResponse)
async def download_knowledge_api(knowledge_id: str, user: Annotated[UserSchema, Depends(get_current_user)]):
    knowledge_content = await download_knowledge_content(knowledge_id, user)  # Sử dụng hàm download_content
    return StreamingResponse(BytesIO(knowledge_content), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={knowledge_id}.txt"})

@router.delete("/{knowledge_id}")
async def delete_knowledge_api(knowledge_id: str, user: Annotated[UserSchema, Depends(get_current_user)]):
    delete_current_knowledge(knowledge_id, user)  # Sử dụng hàm delete_current_knowledge
    return jsonResponseFmt(None, f"Knowledge document {knowledge_id} deleted successfully")
