import requests
import json

def get_filters_with_locations(query: str, category: str, filename: str = "filters_with_locations.json"):
    """
    This function retrieves the main filters and the complete list of neighborhoods from the Divar API,
    then merges and saves them into a single JSON file.

    :param query: The title to search for (e.g., 'Yamaha guitar').
    :param category: The category ID (e.g., 'guitar-bass-amplifier').
    :param filename: The name of the file where the final output will be saved.
    """
    filters_url = 'https://api.divar.ir/v8/postlist/w/filters'
    locations_url = 'https://api.divar.ir/v8/w/lazy-multi-select-hierarchy-options'
    
    headers = {'Content-Type': 'application/json'}

    # Data structure for the first request (filters)
    filters_payload = {
        'city_ids': ['1'],
        'source_view': 'SEARCH_BAR_QUERY_SUGGESTION',
        'data': {
            'form_data': {'data': {'category': {'str': {'value': category}}}},
            'server_payload': {
                '@type': 'type.googleapis.com/widgets.SearchData.ServerPayload',
                'additional_form_data': {'data': {'sort': {'str': {'value': 'sort_date'}}}},
            },
            'query': query,
        },
    }

    try:
        # --- Step 1: Get the main filters ---
        response_filters = requests.post(filters_url, headers=headers, json=filters_payload)
        response_filters.raise_for_status()
        main_filters_data = response_filters.json()

        # --- Step 2: Find the district widget and extract the payload ---
        district_widget = None
        for widget in main_filters_data.get("page", {}).get("widget_list", []):
            if widget.get("widget_type") == "I_LAZY_MULTI_SELECT_DISTRICT_ROW":
                district_widget = widget
                break
        
        if not district_widget:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(main_filters_data, f, ensure_ascii=False, indent=4)
            return main_filters_data

        lazy_payload = district_widget.get("data", {}).get("lazy_payload")
        if not lazy_payload:
            return main_filters_data

        # --- Step 3: Get the list of neighborhoods ---
        locations_payload = {'payload': lazy_payload}
        response_locations = requests.post(locations_url, headers=headers, json=locations_payload)
        response_locations.raise_for_status()
        locations_data = response_locations.json()

        # --- Step 4: Merge the list of neighborhoods into the main structure ---
        # Add the list of neighborhoods to the corresponding widget in the main JSON
        district_widget["data"]["loaded_options"] = locations_data.get("options")
        
        # Save the final JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(main_filters_data, f, ensure_ascii=False, indent=4)
            
        return main_filters_data

    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass
    
    return None

# --- How to use the function ---
if __name__ == '__main__':
    search_title = 'گیتار یاماها'
    search_category = 'guitar-bass-amplifier'
    output_filename = 'filters_with_locations.json'

    # Call the function to get and save filters along with neighborhoods
    get_filters_with_locations(search_title, search_category, output_filename)