from typing import Union, List
import glob
from tqdm import tqdm
import multiprocessing
import pandas as pd
from langchain_community.document_loaders import CSVLoader as LangchainCSVLoader
from langchain.schema import Document


# Helper function to remove non-UTF-8 characters from text
def remove_non_utf8_characters(text: str) -> str:
    return " ".join([char for char in text if ord(char) < 128])


# Function to load a single CSV and clean its content
def load_csv(csv_file: str):
    csv_loader = LangchainCSVLoader(csv_file)
    csvs = csv_loader.load()

    # Clean CSV page content by removing non-UTF-8 characters
    for csv in csvs:
        csv.page_content = remove_non_utf8_characters(csv.page_content)

    return csvs  # Trả về danh sách các Document


# Class for splitting CSV data into chunks (rows)
class CSVTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 0) -> None:
        """
        Splits CSV data into chunks based on the number of rows.
        
        Parameters:
        chunk_size (int): Number of rows per chunk.
        chunk_overlap (int): Number of overlapping rows between consecutive chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def __call__(self, csv_file: str) -> List[pd.DataFrame]:
        """
        Splits the CSV file into chunks of rows.

        Parameters:
        csv_file (str): Path to the CSV file.
        
        Returns:
        List[pd.DataFrame]: List of DataFrame chunks.
        """
        df = pd.read_csv(csv_file, encoding='ISO-8859-1')

        chunks = []
        # Create chunks with overlap
        for start_row in range(0, len(df), self.chunk_size - self.chunk_overlap):
            end_row = start_row + self.chunk_size
            chunk = df.iloc[start_row:end_row]  # Get the chunk of rows
            chunks.append(chunk)

        return chunks


# CSV Processor class for loading and splitting CSV files
class CSVProcessor:
    def __init__(self, split_kwargs: dict = {"chunk_size": 300, "chunk_overlap": 0}, file_type: str = None) -> None:
        self.split_kwargs = split_kwargs
        self.splitter = CSVTextSplitter(**split_kwargs)
        self.file_type = file_type

    def load_and_split(self, csv_files: Union[str, List[str]], workers: int = 1):
        """
        Load and split CSV files into chunks.
        """
        if isinstance(csv_files, str):
            csv_files = [csv_files]

        # Use multiprocessing to load CSV files in parallel
        num_processes = min(multiprocessing.cpu_count(), workers)
        with multiprocessing.Pool(processes=num_processes) as pool:
            loaded_csvs = []
            total_files = len(csv_files)

            with tqdm(total=total_files, desc="Loading CSV files", unit='file') as pbar:
                for result in pool.imap_unordered(load_csv, csv_files):
                    loaded_csvs.extend(result)  # Collect the loaded CSVs
                    pbar.update(1)

        # Convert loaded csvs into Document objects
        documents = []
        for csv_doc in loaded_csvs:
            documents.append(csv_doc)  # Directly append the loaded Document

        return documents  # Trả về danh sách Document

    def load_dir(self, dir_path: str, workers: int = 1):
        """
        Load all CSV files from a directory and split them into chunks.
        """
        csv_files = glob.glob(f"{dir_path}/*.csv")
        assert len(csv_files) > 0, f"No CSV files found in {dir_path}"
        return self.load_and_split(csv_files, workers=workers)
