from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langserve import add_routes

from src.base.model import get_llm
from src.rag.main import build_rag_chain, InputQA, OutputQA

chat_history = []

llm = get_llm()
csv_dir ="D:/Hoc_Hoang/EXE201/UpSale/Data_Source"

##--Chain--

genai_chain = build_rag_chain(llm, csv_dir, "csv")

## APP - FAST API 

app = FastAPI(
    title="UpSale",
    description="A conversational AI for sales assistants",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

## ROUTES

@app.get("/check")
async def check():
    return {"status": "ok"}

@app.post("/ask", response_model=OutputQA)
async def ask(input: InputQA):
    answer = genai_chain.invoke(input.question)
    return {"answer": answer}

# Langserve Routes - Playground
add_routes(app,
           genai_chain,
           playground_type="default",
           path ="/ask")