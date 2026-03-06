from langchain.tools import tool

@tool
def currency_converter(amount: float, from_curr: str, to_curr: str) -> str:
  """
  Converts travel expenses between USD, and INR.
  Use this when user asks for budget conversions.
  """

rates = {"USD": 1.0, "EUR": 0.92, "INR": 83.0}
try:
  res = amount * (rates[to_curr.upper()] / rates[from_curr.upper()]
  return f"{amount} {from_curr} is approximately {res:.2f} {to_curr}"
except KeyError:
    return "Unsupported currency. Please use USD, EUR, or INR."
                  
