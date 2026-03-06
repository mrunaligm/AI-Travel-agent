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
