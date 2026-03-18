import os, time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
def process_pdf(file):
    with open("temp.pdf", "wb") as f:
        f.write(file.getbuffer())
    
    loader = PyPDFLoader("temp.pdf")
    data = loader.load()
    
    # Larger chunks to avoid 429 rate limit errors
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chunks = text_splitter.split_documents(data)
    
    # 2026 Stable Models
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Clear and recreate vector store
    vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
    return vector_store.as_retriever()

    # agent has 3 tools
    tools = [travel_search, currency_conerter, query_travel_docs]


import sqlite3
import sys

# Workaround for SQLite version issues on Streamlit Cloud
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

def init_db():
    conn = sqlite3.connect('travel_assistant.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            destination TEXT,
            results TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_search(query, destination, results):
    conn = sqlite3.connect('travel_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_history (query, destination, results) VALUES (?, ?, ?)",
        (query, destination, str(results))
    )
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('travel_assistant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT query, destination, timestamp FROM search_history ORDER BY timestamp DESC LIMIT 5")
    data = cursor.fetchall()
    conn.close()
    return data
