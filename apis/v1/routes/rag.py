from typing import Annotated
from fastapi import APIRouter, Depends
from ..schemas.user_schema import UserSchema
from ..middlewares.auth_middleware import get_current_user
from ..controllers.rag_controller import RAGController
from ..schemas.knowledge_schema import KnowledgeSchema
from ..utils.response_fmt import jsonResponseFmt
from ..configs.llm_config import gpt_model, gemini_model

router = APIRouter(prefix="/rag", tags=["RAG"])

# Initialize the RAG controller
rag_controller = RAGController()

@router.post("/ask")
async def ask_question(
    document_id: str,
    question: str,
    user: Annotated[UserSchema, Depends(get_current_user)]
):
    """
    Ask a question regarding a specific knowledge document.
    
    Parameters:
    - document_id: The ID of the document for context.
    - question: The user's question.
    - user: The current authenticated user.

    Returns:
    - dict: Contains the question and the generated answer.
    """
    try:
        response = await rag_controller.get_response(question, document_id, user)
        return jsonResponseFmt(response)
    except Exception as e:
        return jsonResponseFmt(None, str(e), status_code=500)

@router.post("/set-llm")
async def set_llm(
    llm_name: str,
    user: Annotated[UserSchema, Depends(get_current_user)]
):
    """
    Set the LLM to be used for answering questions.
    
    Parameters:
    - llm_name: The name of the LLM to set (e.g., 'gpt' or 'gemini').
    - user: The current authenticated user.

    Returns:
    - dict: Confirmation that the LLM has been set.
    """
    try:
        if llm_name not in ["gpt", "gemini"]:
            return jsonResponseFmt(None, "Invalid LLM name", status_code=400)
        
        llm_model = gpt_model if llm_name == "gpt" else gemini_model
        rag_controller.set_llm(llm_model)
        return jsonResponseFmt({"status": f"LLM set to {llm_name} successfully."})
    except Exception as e:
        return jsonResponseFmt(None, str(e), status_code=500)
