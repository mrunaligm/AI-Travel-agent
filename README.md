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

# AI Travel Concierge (Track A week 5-6)
An intelligent travel assistant that uses AI to search for flights, store search history, and generate personalized travel itineraries.

## 🚀 Project Overview
This project is part of an 8-week AI Agent development curriculum. It demonstrates the integration of Large Language Models (LLMs) with real-world APIs and persistent storage using SQLite.

### Key Features
- **Real-time Flight Search:** Integrates with the Google Flights API (via SerpApi).
- **AI-Powered Itineraries:** Uses Google Gemini (1.5-Flash) to generate 2-day travel plans.
- **Search Persistence:** Saves all user queries and flight results to a local SQLite database.
- **Secure Architecture:** Handles API credentials safely using environment secrets.

---

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **AI Framework:** LangChain & Google Generative AI (Gemini)
- **API Integration:** SerpApi (Google Flights Engine)
- **Database:** SQLite3
- **Interface:** Streamlit (Web UI)
- **Deployment:** Streamlit Cloud

---

## 📋 Prerequisites
Before running the project, you will need:
1. A **Google AI Studio API Key** (for Gemini).
2. A **SerpApi Key** (for flight searches).

---

## ⚙️ Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME

# week 7-8

## Features
-**Conversational AI** : inetractive chat interface
-**Smart search** : structured input for destination, budget and time
-**Visual search** : recommended cards for flights and accomodation
-**Persistant history** : integrated SQlite database to view past searches
-**Clean UI** : production ready dashboard with sidebar navigation

## Tech stack

-**Framework** : langchain and llm
-**Frontend** : Streamlit
-**Database** : SQLite
-**Language** : python 3.x
-**deployment** : streamlit cloud
