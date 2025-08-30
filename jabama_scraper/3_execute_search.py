# file: 3_perform_search.py

import requests
import json

def receive_result(
    api_keyword: str,
    selected_filters: dict,
    results_count: int = 10,
    output_filename="final_cleaned_results.json"
):
    """
    Executes a search with a specific keyword and filters, then saves the
    structured results to a dictionary in a JSON file.

    Args:
        api_keyword (str): The exact destination keyword.
        selected_filters (dict): A dictionary of selected filters.
        results_count (int): The desired number of results.
        output_filename (str): The name for the final output file.
    """
    if selected_filters is None:
        selected_filters = {}

    api_url = f"https://gw.jabama.com/api/v4/keyword/{api_keyword}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
    
    json_data = {"page-size": results_count}
    json_data.update(selected_filters)

    try:
        response = requests.post(api_url, headers=headers, json=json_data, timeout=20)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException:
        return # Fail silently on request error

    raw_items = api_data.get("result", {}).get("items", [])
    if not raw_items:
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump({}, f) # Save an empty object if no results
        except IOError:
            pass # Fail silently on file error
        return

    cleaned_results_dict = {}
    
    # Use enumerate to create a 1-based index for the keys
    for index, item in enumerate(raw_items, start=1):
        item_type = item.get('type')
        item_code = item.get('code')
        details_url = "URL not available"
        if item_type and item_code:
            try:
                # Ensure item_code is an integer before formatting
                slug = f"{item_type}-{int(item_code)}"
                details_url = f"https://www.jabama.com/stay/{slug}"
            except (ValueError, TypeError):
                # Handle cases where item_code might not be a valid number
                pass

        amenities_list = [amenity.get('name') for amenity in item.get('amenities', [])]

        cleaned_item = {
            "name": item.get('name'),
            "details_page_url": details_url,
            "place_id": item.get('id'),
            "type": item_type,
            "location": {
                "province": item.get('location', {}).get('province'),
                "city": item.get('location', {}).get('city'),
            },
            "price": {
                "per_night_rials": item.get('price', {}).get('perNight'),
                "description": item.get('price', {}).get('text'),
                "discount_percent": item.get('price', {}).get('discountPercent', 0)
            },
            "rating": {
                "score": item.get('rate_review', {}).get('score', 0),
                "count": int(item.get('rate_review', {}).get('count', 0)),
            },
            "capacity": {
                "base": int(item.get('capacity', {}).get('base', 0)),
                "extra": int(item.get('capacity', {}).get('extra', 0)),
                "total": int(item.get('capacity', {}).get('base', 0)) + int(item.get('capacity', {}).get('extra', 0))
            },
            "specs": {
                "bedrooms": int(item.get('accommodationMetrics', {}).get('bedroomsCount', 0)),
                "bathrooms": int(item.get('accommodationMetrics', {}).get('bathroomsCount', 0)),
                "building_size_sqm": item.get('accommodationMetrics', {}).get('buildingSize'),
                "area_size_sqm": item.get('accommodationMetrics', {}).get('areaSize'),
            },
            "main_image_url": item.get('image'),
            "all_images_url": item.get('images', []),
            "amenities": amenities_list,
            "tags": item.get('tags', []),
            "description": item.get('description', '').strip()
        }
        
        # Create a key (e.g., "result_1") and add the item to the dictionary
        result_key = f"result_{index}"
        cleaned_results_dict[result_key] = cleaned_item

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(cleaned_results_dict, f, indent=4, ensure_ascii=False)
    except IOError:
        pass # Fail silently on file write error

if __name__ == "__main__":
    final_api_keyword = "city-ramsar"
    final_selections = {
        "types": ["villa"],
        "amenities": ["swimming-pool"],
        "scores": ["4.0-5.0"]
    }
    number_of_results_to_show = 3
    
    receive_result(
        api_keyword=final_api_keyword,
        selected_filters=final_selections,
        results_count=number_of_results_to_show
    )