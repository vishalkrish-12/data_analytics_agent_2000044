from langchain.tools import tool
from pydantic import BaseModel, Field

class WebScraperInput(BaseModel):
    url: str = Field(..., description="The URL to scrape")

@tool("WebScraperTool", args_schema=WebScraperInput, return_direct=True)
def WebScraperTool(url: str) -> str:
    """
    Downloads and extracts tables from a given web page.
    Input: The URL.
    Returns: The first wikitable/table as CSV, for further analysis.
    """
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd

    url = url.strip().strip("'\"")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return f"Error fetching URL: {e}"

    soup = BeautifulSoup(resp.content, 'html.parser')
    table = soup.find('table', class_='wikitable') or soup.find('table')
    if not table:
        return "No table found at the provided URL."
    rows = []
    for row in table.find_all('tr'):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
        if cells:
            rows.append(cells)
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df.to_csv(index=False)