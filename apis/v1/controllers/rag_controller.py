from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import AnyStr
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from fastapi import HTTPException, status
from ..schemas.user_schema import UserSchema
from ..configs.llm_config import gpt_model, gemini_model
from ..schemas.knowledge_schema import KnowledgeSchema
from ..schemas.project_schema import ProjectSchema
from ..providers import vector_db


class StrOutputParser(StrOutputParser):
    def __init__(self) -> None:
        super().__init__()

    def parse(self, text: str) -> str:
        return self.extract_answer(text)

    def extract_answer(self, text_response: str, pattern: str = r'Answer:\s*(.*)') -> str:
        match = re.search(pattern, text_response, re.DOTALL)
        return match.group(1).strip() if match else text_response


class RAGController:
    def __init__(self, llm=None) -> None:
        """
        Initialize the RAGController with a default LLM.
        Parameters:
        llm: The large language model to be used for answering questions. Default is gemini_model.
        """
        self.llm = llm or gemini_model  # Set default LLM to gemini
        self.str_parser = StrOutputParser()

    def set_llm(self, llm) -> None:
        """Set the LLM for answering questions."""
        self.llm = llm

    def _validate_permission(self, project_id: AnyStr, user: UserSchema):
        """Validate project ID against user's permissions."""
        if project_id not in user.projects and project_id not in user.shared:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this project."
            )

        project = ProjectSchema.find_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found."
            )
        return project

    def create_information_extractor_prompt(self, user_system_message: str) -> ChatPromptTemplate:
        """Create a prompt template for information extraction."""
        return ChatPromptTemplate(
            [
                SystemMessagePromptTemplate(user_system_message),
                HumanMessagePromptTemplate("Question: {question}. Context: {context}")
            ]
        )

    def format_docs(self, documents) -> str:
        """Format retrieved documents for the prompt."""
        return "\n".join(doc.page_content for doc in documents)

    async def get_response(self, question: str, document_id: str, current_user: UserSchema):
        """
        Asynchronously get answers to a question based on a document, ensuring permission.
        
        Parameters:
        - question: The user's question.
        - document_id: The ID of the document for context.
        - current_user: The user asking the question (for validation).

        Returns:
        - dict: Contains the original question and extracted answers.
        """
        # Fetch knowledge document and validate permission
        document_data = KnowledgeSchema.find_by_id(document_id)
        self._validate_permission(document_data.project_id, current_user)

        # Load the vector database collection
        await vector_db.load_collection

        # Retrieve previous messages from Redis
        message_history = self.get_message_history(current_user.user_id)

        # Format the message history for context
        context = "\n".join([f"Q: {q} A: {a}" for q, a in message_history.items()])

        # Set up retriever and chain for question answering
        retriever = vector_db.create_retriever()
        prompt_template = self.create_information_extractor_prompt("System message here")  # Define system message as needed

        # Modify prompt to include the context
        human_prompt = f"Previous context:\n{context}\n\nQuestion: {question}. Context: {self.format_docs(retriever.retrieve(document_data))}"
        formatted_prompt = HumanMessagePromptTemplate(human_prompt)

        chain = prompt_template | self.llm | self.str_parser
        rag_chain = {"context": retriever | self.format_docs, "question": RunnablePassthrough()} | chain

        # Get answers asynchronously
        answers = await rag_chain.invoke(question)

        # Save the question and answer to message history
        self.save_message_history(current_user.user_id, question, answers)

        return {
            "question": question,
            "answers": answers,
        }

