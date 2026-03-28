# app.py
import streamlit as st
import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("searches.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS searches (query TEXT, result TEXT)")

def save_search(query, result):
    c.execute("INSERT INTO searches VALUES (?, ?)", (query, result))
    conn.commit()

# -----------------------------
# Tool Definitions
# -----------------------------
def search_tool(query):
    # Placeholder for web search API integration
    return f"[WebSearch] Results for: {query}"

def flight_api(query):
    # Placeholder for flight API integration
    return f"[FlightAPI] Flight info for: {query}"

def hotel_api(query):
    # Placeholder for hotel API integration
    return f"[HotelAPI] Hotel info for: {query}"

tools = [
    Tool(name="WebSearch", func=search_tool, description="Search the web"),
    Tool(name="FlightAPI", func=flight_api, description="Get flight info"),
    Tool(name="HotelAPI", func=hotel_api, description="Get hotel info"),
]

# -----------------------------
# LLM + Agent Setup
# -----------------------------
llm = ChatOpenAI()
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="AI Travel Concierge", layout="wide")
st.title("🌍 AI Travel Concierge")
st.markdown("Your personal assistant for travel planning, research, and itinerary generation.")

# Document Upload (RAG)
uploaded_file = st.file_uploader("Upload a document (optional)", type=["pdf", "txt"])
qa_chain = None
if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts([text], embeddings)
    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(), vectorstore.as_retriever()
    )
    st.success("Document uploaded and indexed!")

# Chat Interface
query = st.text_input("Ask me anything about your trip:")
if query:
    if qa_chain:
        response = qa_chain.run(query)
    else:
        response = agent.run(query)

    save_search(query, response)
    st.success("Here’s what I found:")
    st.write(response)

# Export Searches
if st.button("Export Searches"):
    c.execute("SELECT * FROM searches")
    rows = c.fetchall()
    export_text = "\n".join([f"{q} -> {r}" for q, r in rows])
    st.download_button("Download Searches", export_text, file_name="searches.txt")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Built with LangChain + Streamlit | Demo Project")
