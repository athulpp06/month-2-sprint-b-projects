from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import rag

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    top_k: int = 4

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    added = sum(rag.ingest(f.file, f.filename) for f in files)
    return {"chunks_added": added}

@app.post("/ask")
async def ask(req: AskRequest):
    ans, sources = rag.answer(req.question, req.top_k)
    return {"answer": ans, "sources": sources}
