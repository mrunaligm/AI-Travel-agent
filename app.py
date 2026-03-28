import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Database Setup (Requirement: SQLite for saving searches) 
def init_db():
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS searches 
                 (id INTEGER PRIMARY KEY, timestamp TEXT, destination TEXT, query TEXT)''')
    conn.commit()
    conn.close()

def save_search(destination, query):
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO searches (timestamp, destination, query) VALUES (?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), destination, query))
    conn.commit()
    conn.close()

# 2. UI Configuration (Requirement: Clean interface with Results Cards) 
st.set_page_config(page_title="AI Travel Concierge", layout="wide")

def display_travel_card(title, price, description, link_text="Book Now"):
    """Creates a visual card for search results [cite: 84]"""
    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <h4>{title}</h4>
            <p><b>Estimated Cost:</b> {price}</p>
            <p>{description}</p>
            <button style="background-color: #ff4b4b; color: white; border: none; padding: 8px 15px; border-radius: 5px;">
                {link_text}
            </button>
        </div>
        """, unsafe_allow_index=True)

# 3. Main Application Logic
def main():
    init_db()
    
    st.title("🌍 AI Travel Concierge")
    st.markdown("Your personal assistant for flights, hotels, and itineraries.")

    # Sidebar for Search History [cite: 72, 85]
    with st.sidebar:
        st.header("Recent Searches")
        conn = sqlite3.connect('travel_app.db')
        history = pd.read_sql_query("SELECT destination, timestamp FROM searches ORDER BY id DESC LIMIT 5", conn)
        st.table(history)
        
        if st.button("Clear History"):
            conn.execute("DELETE FROM searches")
            conn.commit()
            st.rerun()
        conn.close()

    # Input Validation (Requirement: Basic input validation) 
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("Where to?")
        with col2:
            budget = st.selectbox("Budget Level", ["Economy", "Mid-range", "Luxury"])
        
        query = st.text_area("Tell us about your dream trip...")
        submit = st.form_submit_button("Generate Itinerary")

    if submit:
        if not dest or not query:
            st.error("Please provide both a destination and details about your trip!")
        else:
            save_search(dest, query)
            
            # Simulated Agent Response (Integrate your LangChain agent here) [cite: 100]
            with st.spinner("Analyzing travel options..."):
                st.subheader(f"Custom Itinerary for {dest}")
                
                # Layout for Results Display [cite: 84]
                col_a, col_b = st.columns(2)
                with col_a:
                    display_travel_card(f"Flight to {dest}", "$450", "Round-trip with 1 stopover.")
                with col_b:
                    display_travel_card("Central Boutique Hotel", "$120/night", "Top-rated stay in the heart of the city.")

                st.info(f"### Suggested Daily Plan\n1. Morning: Visit local landmarks.\n2. Afternoon: {query[:50]}...\n3. Evening: Dinner at a traditional restaurant.")

# 4. Chat Interface (Requirement: Chat interface) 
st.divider()
st.subheader("💬 Chat with your Agent")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a follow-up question:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = f"I've updated your {dest if 'dest' in locals() else 'trip'} plans based on: {prompt}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
