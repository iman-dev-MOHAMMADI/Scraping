import requests
import json

def find_key_recursive(data, target_key):
    """
    Recursively searches for a specific key in a nested data structure (dictionary/list).
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            result = find_key_recursive(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_recursive(item, target_key)
            if result is not None:
                return result
    return None


def extract_post_data(raw_json_data: dict, num_results: int = None) -> dict:
    """
    Converts raw JSON data into a clean, structured dictionary.
    This function intelligently searches for the 'list_widgets' key in the response and limits the number of results.
    """
    processed_results = {}
    post_counter = 1

    widget_list = find_key_recursive(raw_json_data, 'list_widgets')

    if not widget_list or not isinstance(widget_list, list):
        return {}

    for widget in widget_list:
        # If the number of results is specified and the counter exceeds it, stop the loop
        if num_results is not None and post_counter > num_results:
            break

        if widget.get("widget_type") == "POST_ROW":
            data = widget.get("data", {})
            action_payload = data.get("action", {}).get("payload", {})
            web_info = action_payload.get("web_info", {})
            server_info = widget.get("action_log", {}).get("server_side_info", {}).get("info", {})

            post_info = {
                "token": data.get("token"),
                "title": data.get("title"),
                "district_persian": web_info.get("district_persian"),
                "city_persian": web_info.get("city_persian"),
                "image_url": data.get("image_url"),
                "bottom_description_text": data.get("bottom_description_text"),
                "has_chat": data.get("has_chat"),
                "red_text": data.get("red_text"),
                "middle_description_text": data.get("middle_description_text"),
                "has_divider": data.get("has_divider"),
                "image_count": data.get("image_count"),
                "top_description_text": data.get("top_description_text"),
                "should_indicate_seen_status": data.get("should_indicate_seen_status"),
                "sort_date": server_info.get("sort_date")
            }
            
            processed_results[f"result_{post_counter}"] = post_info
            post_counter += 1
            
    return processed_results


def search_divar_posts(query: str, category: str, num_results: int = None, filters: dict = None, processed_filename: str = "processed_results.json"):
    """
    Performs the search, limits the results to the specified number, and saves only the processed results.
    """
    api_url = 'https://api.divar.ir/v8/postlist/w/search'
    headers = {'Content-Type': 'application/json'}

    search_payload = {
        'city_ids': ['1'],
        'source_view': 'SEARCH_BAR_QUERY_SUGGESTION',
        'search_data': {
            'form_data': { 'data': { 'category': { 'str': { 'value': category } } } },
            'server_payload': {
                '@type': 'type.googleapis.com/widgets.SearchData.ServerPayload',
                'additional_form_data': { 'data': { 'sort': { 'str': { 'value': 'sort_date' } } } }
            },
            'query': query
        }
    }

    if filters and isinstance(filters, dict):
        search_payload['search_data']['form_data']['data'].update(filters)

    try:
        response = requests.post(api_url, headers=headers, json=search_payload)
        response.raise_for_status()

        raw_results = response.json()
        
        # Pass the number of results parameter to the processing function
        processed_data = extract_post_data(raw_results, num_results)
        
        if not processed_data:
             return None

        with open(processed_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
        
        return processed_data

    except requests.exceptions.HTTPError:
        pass
    except Exception:
        pass

    return None

# --- How to use the function ---
if __name__ == '__main__':
    search_title = 'گیتار یاماها'
    search_category = 'guitar-bass-amplifier'
    # Specify the desired number of results
    num_results_to_show = 5
    
    # Call the function with the new parameter to specify the number of results
    search_divar_posts(
        search_title, 
        search_category,
        num_results=num_results_to_show,
        processed_filename="result.json"
    )