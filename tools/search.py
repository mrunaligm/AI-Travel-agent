from langchain_community.tools import DuckDuckGOSearchRun
from langchain.tools import tool

@tool
def travel_search(query: str):
  """
  Search web for real-time travel information,
  including hotel prices, flight status, and local attractions.
  """

search = DuckDuckGoSearchRun()
return search.run(query)

from search import FlightSearcher

searcher = FlightSearcher()
flight_data = searcher.get_flights(dep_city, arr_city, travel_date)

if flight_data:
    st.success(f"Found {len(flight_data)} flights!")
    # Proceed to save to SQLite and run RAG...
