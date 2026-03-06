# AI Travel Concierge

An AI-powered Travel Assistant using:
- Streamlit
- LangChain
- Gemini (Google Generative AI)
- ChromaDB
- RAG Architecture

## Features
- Upload travel guide PDF
- Ask trip-related questions
- Context-aware answers using RAG

## How to Run

1. Install requirements
pip install -r requirements.txt

2. Add your GOOGLE_API_KEY in Streamlit Secrets

3. Run the app
streamlit run app.py

## Week 4 Milestone features

- **Live Travel Search** Integarated with DuckDuckGo for real-time and flight information.
- **Budget Calculator** custom tool for converting expenses between USD, EUR, and INR.
- **Reasoning Engine** uses OpenAI/Gemini to decide which tool to call based on user internet.

## Setup

1. Clone the repo.
2. Install dependencies: 'pip install -r requirements.txt'
3. Add your API key to a '.env' file:
    'OPENAI_API_KEY=your_key_here'

## Roadmap

-[x] Week 3: Agentic Workflow
-[x] Week 4: Tool Integration
-[ ] Week 5: SQLite Persistent & user memory
-[ ] Week 6: Streamlit UI Finalization
