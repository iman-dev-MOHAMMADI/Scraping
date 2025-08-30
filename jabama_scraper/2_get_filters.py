# file: 2_fetch_filters.py

import requests
import json

def receive_filters(api_keyword: str, output_filename="available_filters.json"):
    """
    Fetches the available search filters for a given API keyword and saves them to a file.

    Args:
        api_keyword (str): The specific destination keyword (e.g., 'city-ramsar').
        output_filename (str): The name of the output JSON file.
    """
    api_url = f"https://gw.jabama.com/api/v4/keyword/{api_keyword}"
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    # A minimal payload is sufficient to get the filter structure.
    json_data = {"page-size": 1}

    try:
        response = requests.post(api_url, headers=headers, json=json_data, timeout=15)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException:
        return # Fail silently on API error

    raw_filters = api_data.get("result", {}).get("filters", [])
    if not raw_filters:
        return # No filters found

    available_filters = {}

    for f in raw_filters:
        field_name = f.get('field')
        filter_type = f.get('filter-type')
        filter_name = f.get('name')

        if not field_name:
            continue

        # For filters without a fixed list of options (e.g., pax count, price range)
        if filter_type in ['Pax', 'Range', 'Bool']:
            filter_info = {'name': filter_name, 'type': filter_type}
            if f.get('filter-range'):
                filter_info['range'] = f['filter-range'] # Add default price range
            available_filters[field_name] = filter_info
            continue

        # For filters with a list of options (CheckList, Score, Rooms)
        options = []
        filter_options_list = f.get('filters', [])

        # Special handling for nested city filters
        if field_name == 'location-cities':
            for province_option in filter_options_list:
                if province_option.get('sub-key'):
                    for city_option in province_option['sub-key']:
                        options.append({
                            'name': city_option.get('persian-name'),
                            'key': city_option.get('key')
                        })
        # For all other list-based filters
        else:
            for option in filter_options_list:
                options.append({
                    'name': option.get('persian-name'),
                    'key': option.get('key')
                })

        if options:
            available_filters[field_name] = {
                'name': filter_name,
                'type': filter_type,
                'options': options
            }

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(available_filters, f, indent=4, ensure_ascii=False)
    except IOError:
        pass # Fail silently on file writing error

if __name__ == "__main__":
    # This keyword would be selected from the output of the first script (suggestions.json).
    # Using a keyword that is known to have city filters for testing purposes.
    chosen_api_keyword = "stays-tehran-villa"

    # Example for a province:
    # chosen_api_keyword = "province-khuzestan"

    receive_filters(chosen_api_keyword)