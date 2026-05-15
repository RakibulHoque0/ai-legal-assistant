import streamlit as st
import requests
import os
import json

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Legal Case Assistant", layout="wide")

st.title("⚖️ Grounded Legal Document Drafting Assistant")
st.markdown("---")

# Sidebar - Preferences
with st.sidebar:
    st.header("Operator Preferences")
    if os.path.exists("preferences.json"):
        with open("preferences.json", "r") as f:
            st.json(json.load(f))
    else:
        st.info("No preferences learned yet.")

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Upload & Process")
    uploaded_file = st.file_uploader("Upload Legal PDF", type=["pdf"])
    
    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("OCR & Chunking in progress..."):
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{BASE_URL}/upload", files={"file": (uploaded_file.name, uploaded_file.getvalue())})
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Document processed! {data['page_count']} pages indexed.")
                    
                    # Show Structured Fields
                    st.subheader("📌 Extracted Data")
                    st.write(data["structured_fields"])
                    
                    # Show Warnings
                    if data["low_confidence_pages"]:
                        st.warning(f"⚠️ Low OCR confidence on pages: {', '.join(map(str, data['low_confidence_pages']))}. Please verify extracts.")
                else:
                    st.error("Processing failed.")

    st.header("2. Retrieval & Draft")
    query = st.text_input("What should the summary focus on?", "Key parties and agreement dates")
    
    if st.button("Generate Grounded Summary"):
        with st.spinner("Querying FAISS & Drafting..."):
            response = requests.post(f"{BASE_URL}/summarize", json={"query": query})
            if response.status_code == 200:
                data = response.json()
                st.session_state["draft"] = data["draft"]
                st.session_state["chunks"] = data["chunks"]
            else:
                st.error("Drafting failed.")

with col2:
    st.header("3. Review & Edit")
    if "draft" in st.session_state:
        final_edit = st.text_area("Edit the draft below:", value=st.session_state["draft"], height=400)
        
        if st.button("Save & Learn Preferences"):
            with st.spinner("Analyzing edits..."):
                response = requests.post(f"{BASE_URL}/learn", json={
                    "original_draft": st.session_state["draft"],
                    "final_edit": final_edit
                })
                if response.status_code == 200:
                    st.success("Preferences updated! Next draft will follow your style.")
                else:
                    st.error("Learning failed.")

    st.header("4. Evidence Inspection")
    if "chunks" in st.session_state:
        for chunk in st.session_state["chunks"]:
            page = chunk.get("metadata", {}).get("page", "Unknown")
            with st.expander(f"Chunk {chunk['chunk_index']} (Page {page}) - Distance: {chunk.get('distance', 0):.4f}"):
                st.write(chunk["text"])
