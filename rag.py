import os, uuid
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("docs", metadata={"hnsw:space": "cosine"})
model = SentenceTransformer("all-MiniLM-L6-v2")

def ingest(file_obj, filename: str) -> int:
    reader = PdfReader(file_obj)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    chunks = [text[i : i + 500] for i in range(0, len(text), 450) if text[i : i + 500].strip()]
    if not chunks:
        return 0
    embs = model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    metas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embs, documents=chunks, metadatas=metas)
    return len(chunks)

def retrieve(question: str, top_k: int = 4):
    count = collection.count()
    if count == 0:
        return []
    q_emb = model.encode([question]).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=min(top_k, count))
    results = []
    if res and res["documents"] and res["documents"][0]:
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            results.append({
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "score": round(1.0 - dist, 4),
                "text": doc,
            })
    return results

def answer(question: str, top_k: int = 4):
    sources = retrieve(question, top_k)
    context = "\n\n".join(s["text"] for s in sources)
    prompt = f"Answer only using the context below. If it isn't there, say you don't know.\n\nContext:\n{context}\n\nQuestion: {question}"
    client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content, sources
