import re
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

class Str_OutputParser(StrOutputParser):
    def __init__(self) -> None:
        super().__init__()
    
    def parse(self, text: str) -> str:
        """
        Parse the LLM's response to extract the answer.
        """
        return self.extract_answer(text)
    
    def extract_answer(self,
                       text_response: str,
                       pattern: str = r'Answer:\s*(.*)') -> str:
        """
        Extract the answer based on a regex pattern.
        
        Parameters:
        text_response (str): The text output from the LLM.
        pattern (str): Regex pattern to identify the answer.
        
        Returns:
        str: Extracted answer or the full response if no match.
        """
        match = re.search(pattern, text_response, re.DOTALL)
        if match:
            answer_text = match.group(1).strip()
            return answer_text
        else:
            return text_response

class Offline_RAG:
    def __init__(self, llm) -> None:
        """
        Initialize the Offline RAG class.
        
        Parameters:
        llm: The large language model to be used for answering questions.
        """
        self.llm = llm
        self.prompt = self.build_prompt()  # Use build_prompt, not self.prompt()
        self.str_parser = Str_OutputParser()

    def build_prompt(self) -> PromptTemplate:
        """
        Build the prompt that will instruct the model to answer questions
        related to product sales based on the context from the CSV files.
        
        Returns:
        PromptTemplate: The prompt template used to generate LLM answers.
        """
        template = """
        
        You are a sales assistant with access to the following information from a product sales CSV dataset:
        
        {context}
        
        Based on this information, answer the following question in detail and with the language that user asking:
        
        {question}
        
        Be concise but provide the necessary details.
        
        Answer:
        """
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def format_docs(self, documents):
        """
        Format the documents retrieved from the retriever to fit the prompt.
        
        Parameters:
        documents: List of documents retrieved.
        
        Returns:
        str: Formatted document text for the prompt.
        """
        return "\n".join([doc.page_content for doc in documents])

    def get_chain(self, retriever):
        """
        Create the RAG (Retrieval-Augmented Generation) chain.
        
        Parameters:
        retriever: The retriever that fetches relevant documents.
        
        Returns:
        rag_chain: A processing pipeline that generates answers based on retrieved context.
        """
        input_data = {
            "context": retriever | self.format_docs,
            "question": RunnablePassthrough()
        }

        rag_chain = (
            input_data
            | self.prompt
            | self.llm
            | self.str_parser
        )
        
        return rag_chain
