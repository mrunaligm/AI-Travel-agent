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

#week 3-4
import streamlit as st
from langchain.agents import AgentExecutor, create_openai_functions_agent
from tools.search import travel_search
from tools.calculator import travel_calculator

tools = [travel_search, travel_calculator]

if "agent_executor" not in st.session_state:
    agent = craete_openai_functions_agent(llm, tools, prompt)
    st.session_state.agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True
    )

user_input = st.chat_input("Ask about hotels or currency conversion...")
if user_input:
    response = st.session_state.agent_executor.invoke({"input": user_input})
    st.write(response["output"])

import streamlit as st
import os
from serpapi import GoogleSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from database_utils import init_db, save_search, get_history

# 1. Setup API Keys from Streamlit Secrets
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

init_db()

st.title("AI Travel Assistant")

# Sidebar for History
st.sidebar.title("Recent Searches")
for h in get_history():
    st.sidebar.write(f"{h[1]} ({h[2][:10]})")

# Main UI
col1, col2, col3 = st.columns(3)
with col1: dep = st.text_input("Departure (e.g., DEL)", value="DEL")
with col2: arr = st.text_input("Arrival (e.g., BOM)", value="BOM")
with col3: date = st.text_input("Date (YYYY-MM-DD)", value="2026-06-15")

if st.button("Search Flights & Plan Itinerary"):
    with st.spinner("Searching..."):
        # API Call
        params = {"engine": "google_flights", "departure_id": dep, "arrival_id": arr, 
                  "outbound_date": date, "api_key": SERPAPI_KEY, "gl": "in", "currency": "INR"}
        search = GoogleSearch(params)
        results = search.get_dict().get("best_flights", [])
        
        # Save to SQLite
        save_search(f"Flights from {dep} to {arr}", arr, results)
        
        # AI Itinerary
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        itinerary = llm.invoke(f"Create a 2-day plan for {arr} given these flights: {results[:2]}")
        
        st.success(f"Found {len(results)} flights!")
        st.markdown(itinerary.content)

import streamlit as st
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

# --- UI CONFIG & DATABASE (Week 5 & 7 Requirements) ---
st.set_page_config(page_title="AI Travel Concierge", page_icon="✈️")
st.title("🌍 Essential AI Travel Assistant")

def init_db():
    conn = sqlite3.connect('travel_concierge.db')
    conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, query TEXT, result TEXT)')
    conn.close()

def save_and_get_history(query=None, result=None):
    conn = sqlite3.connect('travel_concierge.db')
    if query and result:
        conn.execute("INSERT INTO history (query, result) VALUES (?, ?)", (query, result))
        conn.commit()
    data = conn.execute("SELECT query, result FROM history ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return data

init_db()

# --- SIDEBAR HISTORY (Week 8 Polish) ---
st.sidebar.header("📜 Recent Searches")
for h_query, h_result in save_and_get_history():
    with st.sidebar.expander(f"📍 {h_query[:20]}..."):
        st.write(h_result)

# --- MANUAL AGENT LOGIC (Weeks 7-8 Implementation) ---
# Use Streamlit Secrets for the API Key (Requirement for Week 8)
from google.colab import userdata
api_key = userdata.get('GEMINI_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

def search_travel_api(destination: str):
    """Simulates a Travel API call for flights/hotels."""
    return f"Found specialized budget hotels and direct flights for {destination}."

# UI Interaction
user_query = st.text_input("Describe your trip:", placeholder="e.g., 3 days in Paris for art lovers")

if st.button("Generate Itinerary"):
    with st.spinner("Agent is researching..."):
        # Manual ReAct Cycle
        messages = [HumanMessage(content=user_query)]
        ai_response = llm.invoke(messages)
        
        # Display and Save (Track A Core Functionality)
        st.subheader("Your Travel Plan")
        st.write(ai_response.content)
        save_and_get_history(user_query, ai_response.content)
        st.success("Itinerary saved to database!")
