import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Documentation Assistant")
st.title("AI Documentation Assistant")

with st.sidebar:
    st.header("Upload PDFs")
    uploaded = st.file_uploader("Choose PDFs", type=["pdf"], accept_multiple_files=True)
    if st.button("Ingest") and uploaded:
        files = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded]
        res = requests.post(f"{API_URL}/upload", files=files)
        if res.status_code == 200:
            st.success(f"Added {res.json().get('chunks_added', 0)} chunks")
        else:
            st.error("Upload failed")

question = st.text_input("Ask a question:")
if st.button("Ask") and question:
    res = requests.post(f"{API_URL}/ask", json={"question": question, "top_k": 4})
    if res.status_code == 200:
        data = res.json()
        st.subheader("Answer")
        st.write(data.get("answer"))
        st.subheader("Sources")
        for s in data.get("sources", []):
            st.markdown(f"**{s['source']}** (chunk {s['chunk_index']}, score: {s['score']})")
            st.text(s["text"])
    else:
        st.error("Request failed")
