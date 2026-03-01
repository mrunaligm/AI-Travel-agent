import streamlit as st
import os, time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

# 1. Page Configuration & API Setup
st.set_page_config(page_title="AI Travel Concierge", layout="wide")
st.title("AI Travel Concierge (Track A)")

# Use Streamlit Secrets for the API Key
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Please add your GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# 2. Sidebar: Document Upload
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload your Travel Guide (PDF)", type="pdf")
    process_btn = st.button("Process Document")
    
    # Larger chunks to avoid 429 rate limit errors
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chunks = text_splitter.split_documents(data)
    
    # 2026 Stable Models
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Clear and recreate vector store
    vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
    return vector_store.as_retriever()

# 4. Chat Interface
if uploaded_file and process_btn:
    with st.spinner("Analyzing document..."):
        st.session_state.retriever = process_pdf(uploaded_file)
        st.success("Ready to chat!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about your trip!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "retriever" in st.session_state:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=st.session_state.retriever)
        
        with st.chat_message("assistant"):
            response = qa_chain.invoke(prompt)["result"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("Please upload and process a PDF first.")
