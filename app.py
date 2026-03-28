import os, time

os.environ["GEMINI_API_KEY"]=userdata.get('GEMINI_API_KEY')

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA

file_path = "travels_guide.pdf"
try:
  loader = PyPDFLoader(file_path='/content/travels_guide.pdf')
  data = loader.load()
  print(f"successfully loaded {len(data)} pages.")
except Exception as e:
  print(f"error loading pdf: {e}")

  text_splitter=RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
chunks = text_splitter.split_documents(data)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",task_type="retrieval_document")
vector_store = Chroma.from_documents(chunks,embeddings)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0)

rag_chain = RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=vector_store.as_retriever())

from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever(top_k_results=2, lang="en")

query = "the geographical history of attractive tourist places?"

docs = retriever.invoke(query)

for i, doc in enumerate(docs):
    print(f"\n--- Result {i+1} ---")
    print(f"Content:\n{doc.page_content}...")

query = "suggest a 3-day itinerary based on attractions in this guide."
response = rag_chain.invoke(query)
print(f"AI Concierge: {response['result']}")

response = rag_chain.invoke("what are the top attractions?")
print(response["result"])

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",task_type="retrieval_document")
vector_store = Chroma.from_documents(chunks,embeddings,persist_directory="./db")

query="what does this document say about travel safety?"
print(rag_chain.invoke(query)["result"])

import os
from google.colab import userdata

os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY')

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool

search = DuckDuckGoSearchRun()

@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
  """converts travel expenses between different currencies."""
  rates = {"USD": 1.0, "EUR": 0.92, "INR": 83.0}
  if from_currency in rates and to_currency in rates:
    converted = amount * (rates[to_currency] / rates[from_currency])
    return f"{amount} {from_currency} is approximately {converted:.2f} {to_currency}"
  return "currency not supported."

tools = [search, currency_converter]

from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "you are specialized AI travel concierge"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [search, currency_converter]

agent = create_openai_functions_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

def safe_tool_call(query):
  try:
    return agent_executor.invoke({"input": query})
  except Exception as e:
      return f"I encountered a technical glitch: {str(e)}.try rephrasing."

def safe_tool_call(query):
  try:
    return agent_executor.invoke({"input": query})
  except Exception as e:
    return {
      "output": f" Technical Glitch: {str(e)}",
      "status": "error"
      }

user_query = "what is exchange rate of 100 USD to INR and top hotels in Bengaluru?"
response = safe_tool_call(user_query)

final_text = response.get("output", "no response generated.")

print("-" * 30)
print(f"QUERY: {user_query}")
print(f"RESPONSE: {final_text}")
print("-" * 30)

from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

agent = create_openai_functions_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True)

response = safe_tool_call("what is the current exchange rate for 100 USD to INR and what are the top hotels in Bengaluru?")
print(response['output'])

response = safe_tool_call("Find a budget hotel in Bengaluru and convert its price from 3,500 INR to USD.")
print(response['output'])

import sqlite3

def init_db():
  conn = sqlite3.connect('travel_concierge.db')
  cursor = conn.cursor()
  cursor.execute('''
      CREATE TABLE IF NOT EXISTS  search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_query TEXT,
        itinerary TEXT
      )
  ''')
  conn.commit()
  conn.close()

  def save_search(query, result):
    conn = sqlite3.connect('travel_concierge.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO search_history (user_query, itinerary) VALUES (?, ?)", (query, result))
    conn.commit()
    conn.close()

import os
import sqlite3
from dotenv import load_dotenv
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_google_genai import ChatGoogleGenerativeAI

from google.colab import userdata
import os

os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')
TRAVEL_API_KEY = userdata.get('TRAVEL_API_KEY')

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

init_db()

def save_search(query, destination, results):
  conn = sqlite3.connect('travel_assistant.db')
  cursor = conn.cursor()
  cursor.execute("INSERT INTO search_history (query, destination, results) VALUES (?, ?, ?)", (query, destination, str(results)))
  conn.commit()
  conn.close()

  from serpapi import GoogleSearch

def search_flights(departure, arrival, date):
  params = {
      "engine": "google_flights",
      "departure_id": departure,
      "arrival_id": arrival,
      "outbound_date": date,
      "api_key": TRAVEL_API_KEY
  }
  search = GoogleSearch(params)
  results = search.get_dict()

  save_search(f"Flights from {departure}")

  return results.get('best_flights', [])

  from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def flight_search_tool(departure: str, arrival: str, date: str):
  """
  search for best flight options between two cities on a specific date.
  Format: departure and arrival should be 3-letter airport codes (e.g.,'NYC','SFO')
  Date format: YYYY-MM-DD.
  """
  return search_flights(departure, arrival, date)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
tools = [flight_search_tool]
llm_with_tools = llm.bind(tools=tools)

from langchain.tools import tool

@tool
def flight_search_tool(departure: str, arrival: str, date: str):
  """
  search for best flights and save the results to the database.
  """
  results = search.get_dict().get('best_flights', [])
  query_text = f"Flights from {departure} to {arrival}"
  save_search(query_text, arrival, results)
  return results

  import sqlite3
import os
from google.colab import userdata
from langchain.tools import tool
from serpapi import GoogleSearch # Ensure you run !pip install google-search-results
from langchain_google_genai import ChatGoogleGenerativeAI # Ensure you run !pip install langchain-google-genai

# 1. DATABASE SETUP
def init_db():
    conn = sqlite3.connect('travel_assistant.db')
    cursor = conn.cursor() # Corrected: Added () to call the method
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
    cursor = conn.cursor() # Corrected: Added () to call the method
    cursor.execute(
        "INSERT INTO search_history (query, destination, results) VALUES (?, ?, ?)",
        (query, destination, str(results))
    )
    conn.commit()
    conn.close()

# 2. FLIGHT SEARCH TOOL DEFINITION
@tool
def flight_search_tool(departure: str, arrival: str, date: str):
    """
    Search for flights between two cities and save results to the database.
    departure/arrival: 3-letter airport codes (e.g., 'SFO', 'NYC').
    date: YYYY-MM-DD format.
    """
    # Securely retrieve keys from Colab Secrets
    api_key = userdata.get('TRAVEL_API_KEY')

    params = {
        "engine": "google_flights",
        "departure_id": "DEL",
        "arrival_id": "LHR",
        "date": "2026-06-15",
        "gl": "in",
        "hl": "en",
        "currency": "INR",
        "api_key": api_key
    }

    # Corrected: Initialize the 'search' object properly
    search = GoogleSearch(params)
    results_dict = search.get_dict()
    flights = results_dict.get("any_flights", [])
    other = results_dict.get("other_flights", [])
    all_flights = flights + other

    if not all_flights:
        print("no flights found.")

    # Save the successful search to SQLite
    save_search(f"Flights from {departure} to {arrival}", arrival, flights)

    return flights

# 3. INITIALIZATION AND EXECUTION
# Initialize the database file
init_db()

# Set up the LLM (Gemini)
os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Example Test Run
print("Testing the Flight Search Tool...")
try:
    test_results = flight_search_tool.run({
        "departure": "DEL",
        "arrival": "BOM",
        "date": "2026-04-15"
    })
    print(f"Success! Found {len(test_results)} flight options.")

    # 4. ITINERARY GENERATION (Final Step for Week 5-6)
    if test_results:
        prompt = f"Create a simple 2-day travel itinerary for NYC based on these flights: {test_results[:2]}"
        itinerary = llm.invoke(prompt)
        print("\nGenerated Itinerary:\n", itinerary.content)
except Exception as e:
    print(f"Error encountered: {e}")

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
