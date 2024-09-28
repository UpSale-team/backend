from typing import Union, List, Literal
import glob
from tqdm import tqdm
import multiprocessing
from langchain_community.document_loaders import CSVLoader
from langchain_core.indexing import VectorstoreIndexCreator
from langchain.chains import RetrievalQA

import unicodedata 

loader = CSVLoader()

def normalize_text(text):
    return unicodedata.normalize('NFC', text)

def load_csv(csv_file):
    docs = CSVLoader(csv_file).load()
    for doc in docs:
        doc['text'] = normalize_text(doc['text'])
    return docs
index_creator = VectorstoreIndexCreator()
docsearch = index_creator.from_loaders([loader])


def get_num_cpu():