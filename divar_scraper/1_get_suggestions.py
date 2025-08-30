import requests
import json

def get_suggestions(query: str, city_id: str = '1'):
    """
    This function receives a search query, sends it to the Divar API,
    and returns the search suggestions in a clean and simple JSON format.

    :param query: The word you want to search for (e.g., 'guitar').
    :param city_id: The ID of the desired city (default is '1' for Tehran).
    :return: A list of dictionaries containing simplified suggestions or None in case of an error.
    """
    api_url = 'https://api.divar.ir/v8/prediction/w/query'

    # Note: Headers and cookies might be necessary for this request to work correctly in the future.
    # These values can usually be extracted by inspecting browser requests on the Divar website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    cookies = {
        # If needed, add the necessary cookies here
    }

    json_data = {
        'query': query,
        'cities': [city_id],
    }

    try:
        response = requests.post(api_url, headers=headers, cookies=cookies, json=json_data)
        # Check if the request was successful
        response.raise_for_status()

        raw_data = response.json()
        suggestions = raw_data.get('suggestions', [])

        if not suggestions:
            return []

        # Simplify the JSON structure and extract the required information
        clean_suggestions = []
        for suggestion in suggestions:
            # --- Start of changes ---
            # Extract 'value' from the nested JSON path using .get() to prevent errors
            value = suggestion.get('search_data', {}).get('form_data', {}).get('data', {}).get('category', {}).get('str', {}).get('value')

            clean_item = {
                "suggestion_title": suggestion.get('title'),
                "category": suggestion.get('subtitle'),
                "ad_count": suggestion.get('ad_count'),
                "value": value
            }
            # --- End of changes ---
            clean_suggestions.append(clean_item)

        return clean_suggestions

    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None


# --- Example of how to use the function ---

# The desired search query
search_query = "گیتار"

# Get clean and simplified suggestions
simplified_suggestions = get_suggestions(search_query)

# If suggestions are successfully received, save them to a file
if simplified_suggestions:
    # Save the output to a JSON file with a readable format
    try:
        with open('suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(simplified_suggestions, f, ensure_ascii=False, indent=4)

    except IOError:
        pass