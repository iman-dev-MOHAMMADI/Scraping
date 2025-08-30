import requests
import json
import os

def get_divar_post_info(token):
    """
    Retrieves the raw data of a post from the Divar API using its token.
    """
    url = f"https://api.divar.ir/v8/posts-v2/web/{token}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def simplify_post_data(raw_data):
    """
    Converts complex, raw JSON data into a simple and readable structure.
    """
    if not raw_data:
        return None

    try:
        # Create a dictionary for easier access to sections by their name
        sections = {s['section_name']: s['widgets'] for s in raw_data.get('sections', [])}

        # --- Main Information Extraction ---
        
        # 1. Categories (Breadcrumbs)
        breadcrumbs_data = sections.get('BREADCRUMB', [{}])[0].get('data', {})
        categories = [item['title'] for item in breadcrumbs_data.get('parent_items', [])]
        
        # 2. Main Title and Subtitle
        title_data = sections.get('TITLE', [{}])[0].get('data', {})
        title = title_data.get('title')
        subtitle = title_data.get('subtitle')

        # 3. Description
        description = ""
        # Find the description widget within its section
        for widget in sections.get('DESCRIPTION', []):
            if widget.get('widget_type') == 'DESCRIPTION_ROW':
                description = widget.get('data', {}).get('text')
                break

        # 4. Image Links
        image_items = sections.get('IMAGE', [{}])[0].get('data', {}).get('items', [])
        image_urls = [item['image']['url'] for item in image_items if 'image' in item and 'url' in item['image']]

        # 5. Specifications and Details (Complex Section)
        details = {}
        for widget in sections.get('LIST_DATA', []):
            widget_type = widget.get('widget_type')
            data = widget.get('data', {})
            
            if widget_type == 'GROUP_INFO_ROW':
                for item in data.get('items', []):
                    details[item['title']] = item['value']
            
            elif widget_type == 'UNEXPANDABLE_ROW':
                details[data.get('title')] = data.get('value')

            elif widget_type == 'SCORE_ROW':
                details[data.get('title')] = data.get('descriptive_score')

        # 6. Location
        location_data = sections.get('MAP', [{}])[0].get('data', {}).get('location', {})
        location = location_data.get('exact_data', {}).get('point')

        # --- Final Output Construction ---
        simplified_output = {
            "categories": categories,
            "title": title,
            "subtitle": subtitle,
            "description": description.strip() if description else None,
            "image_urls": image_urls,
            "details": details,
            "location": location
        }
        
        return simplified_output

    except (KeyError, IndexError, TypeError):
        return None

def save_to_json_file(data, filename):
    """
    Saves the received data into a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError:
        pass


# --- How to use the code ---
if __name__ == "__main__":
    user_token = "Aa5BgqFj"

    if user_token:
        # 1. Get raw data from the API
        raw_post_data = get_divar_post_info(user_token)

        if raw_post_data:
            # 2. Convert raw data to a simple structure
            simplified_data = simplify_post_data(raw_post_data)

            # 3. Save the simplified data to a JSON file
            if simplified_data:
                json_filename = "detail_post.json"
                save_to_json_file(simplified_data, json_filename)
    else:
        pass