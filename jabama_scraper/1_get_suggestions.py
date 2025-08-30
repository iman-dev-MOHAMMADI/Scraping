# file: 1_fetch_suggestions.py

import requests
import json
from urllib.parse import quote

def receive_suggestions(query: str, output_filename="suggestions.json"):
    """
    Fetches search suggestions from the Jabama API based on a query and saves them to a file.

    Args:
        query (str): The user's search term (e.g., "khuzestan").
        output_filename (str): The name of the output JSON file.
    """
    encoded_query = quote(query)
    api_url = f"https://gw.jabama.com/api/v1/yoda/guest/search/suggestions/{encoded_query}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return  # Fail silently on connection error

    all_suggestions = []
    sections = data.get("result", {}).get("sections", [])
    if not sections:
        return # No suggestions found

    for section in sections:
        for item in section.get("items", []):
            full_title = " ".join([part.get("text", "") for part in item.get("title", [])]).strip()
            all_suggestions.append({
                "title": full_title,
                "description": item.get("description", ""),
                "api_keyword": item.get("url"), # The keyword for the next API call
                "pre_filters": item.get("app", {}).get("preFilters")
            })

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_suggestions, f, indent=4, ensure_ascii=False)
    except IOError:
        pass # Fail silently on file error

if __name__ == "__main__":
    search_query = "بندرانزلی"
    receive_suggestions(search_query)