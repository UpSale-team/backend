from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

def get_llm():
    llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    # temperature=0,
    # max_tokens=None,
    # timeout=None,
    # max_retries=2,
    # # other params...
    )
    return llm

