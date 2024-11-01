import os
from fastapi import HTTPException, status
from langchain_community.document_loaders import Docx2txtLoader, CSVLoader
from typing import List
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Nhập lớp này

# Helper function to remove non-UTF-8 characters from text
def remove_non_utf8_characters(text: str) -> str:
    return "".join([char for char in text if char.isprintable()])

# Load CSV content
def load_csv(csv_file: str):
    loader = CSVLoader(csv_file, encoding="ISO-8859-1")
    docs = loader.load()

    for doc in docs:
        doc.page_content = remove_non_utf8_characters(doc.page_content)

    return docs

# Function to load DOCX, TXT, or CSV files and split content into list of documents
def _load_docx_txt_csv(filepath: str):
    file_extension = os.path.basename(filepath).split('.')[-1].lower()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Sử dụng RecursiveCharacterTextSplitter

    if file_extension == "docx":
        loader = Docx2txtLoader(filepath)
        docs = loader.load_and_split()
        content = "\n".join([doc.page_content for doc in docs])

    elif file_extension == "txt":
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
        content = remove_non_utf8_characters(content)

    elif file_extension == "csv":
        return load_csv(filepath)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type."
        )

    # Sử dụng RecursiveCharacterTextSplitter để chia nội dung
    text_chunks = text_splitter.split_text(content)
    return [{"page_content": chunk} for chunk in text_chunks]

def get_document_content(filepath: str) -> str:
    data = _load_docx_txt_csv(filepath)

    content = ""
    for _data in data:
        if isinstance(_data, dict):
            _content = [line.strip() for line in _data["page_content"].splitlines() if line.strip() != ""]
        else:
            _content = _data
        content += "\n".join(_content) + "\n"

    return content
