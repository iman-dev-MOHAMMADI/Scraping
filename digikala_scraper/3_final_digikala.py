# digikala_report_generator.py

import requests
import json
import re
from typing import Dict, Any, Optional

# --- Constants ---
API_V1_BASE_URL = "https://api.digikala.com/v1/"
API_V2_BASE_URL = "https://api.digikala.com/v2/"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


def product_details(product_url: str) -> Optional[Dict[str, Any]]:
    """
    Generates a complete product report from a Digikala URL.
    This function runs silently and only prints output if an error occurs.

    Args:
        product_url: The URL of the Digikala product page.

    Returns:
        A dictionary containing the full product report, or None if a critical error occurs.
    """
    # --- 1. Extract Product ID from URL ---
    match = re.search(r'dkp-(\d+)', product_url)
    if not match:
        print(f"[Error] Invalid URL or DKP ID not found in URL: {product_url}")
        return None
    product_id = match.group(1)

    # --- 2. Fetch Main Product and Seller Data (v2 API) ---
    product_api_url = f"{API_V2_BASE_URL}product/{product_id}/"
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(product_api_url, headers=headers, timeout=15)
        response.raise_for_status()
        product_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to fetch main product data. Reason: {e}")
        return None

    if 'data' not in product_data or 'product' not in product_data['data']:
        print(f"[Error] Main product data is malformed or missing for ID: {product_id}.")
        return None
    
    product_info = product_data['data']['product']

    # --- 3. Process Product Details ---
    main_variant = product_info.get('default_variant', {})
    
    colors_list = product_info.get('colors')
    available_colors_str = " - ".join([c.get('title', '') for c in colors_list]) if colors_list else "Not specified"
        
    stats = main_variant.get('statistics', {})
    keys_to_remove = {"is_incredible", "is_promotion", "is_locked_for_digiplus", "bnpl_active"}
    filtered_stats = {k: v for k, v in stats.items() if k not in keys_to_remove} if stats else {}
    
    product_summary = {
        "name": product_info.get('title_fa'),
        "id": product_info.get('id'),
        "category": product_info.get('category', {}).get('title_fa'),
        "brand": product_info.get('brand', {}).get('title_fa'),
        "price_info": main_variant.get('price'),
        "available_colors": available_colors_str,
        "statistics": filtered_stats
    }

    # --- 4. Process Seller Offers ---
    unique_offers = []
    seen_sellers = set()
    for variant in product_info.get('variants', []):
        seller_name = variant.get('seller', {}).get('title')
        if seller_name and seller_name not in seen_sellers:
            unique_offers.append({
                "seller_name": seller_name,
                "price": variant.get('price', {}).get('selling_price'),
                "warranty": variant.get('warranty', {}).get('title_fa'),
                "shipping_info": variant.get('shipment_methods', {}).get('description'),
            })
            seen_sellers.add(seller_name)

    # --- 5. Fetch and Process User Feedback (v1 API) ---
    user_feedback = {"comments": [], "questions": []}

    # Fetch comments
    try:
        comments_api_url = f"{API_V1_BASE_URL}rate-review/products/{product_id}/"
        response = requests.get(comments_api_url, params={'page': 1}, headers=headers, timeout=15)
        response.raise_for_status()
        comments_data = response.json()
        if comments_data and 'data' in comments_data:
            raw_comments = (comments_data.get('data', {}).get('comments', []))[:10]
            user_feedback["comments"] = [{"body": c.get('body'), "rating": c.get('rate')} for c in raw_comments]
    except requests.exceptions.RequestException as e:
        print(f"[API Warning] Could not fetch user comments. Reason: {e}")

    # Fetch questions
    try:
        questions_api_url = f"{API_V1_BASE_URL}product/{product_id}/questions/"
        response = requests.get(questions_api_url, headers=headers, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if questions_data and 'data' in questions_data:
            all_raw_questions = questions_data.get('data', {}).get('questions', [])
            for question in all_raw_questions:
                if len(user_feedback["questions"]) >= 10: break
                if question.get('answers'):
                    answer_texts = [ans.get('text') for ans in question.get('answers', [])[:2] if ans.get('text')]
                    if answer_texts:
                        user_feedback["questions"].append({"question": question.get('text'), "answers": answer_texts})
    except requests.exceptions.RequestException as e:
        print(f"[API Warning] Could not fetch user questions. Reason: {e}")

    # --- 6. Assemble and Return the Final Report ---
    full_report = {
        "product_summary": product_summary,
        "seller_offers": unique_offers,
        "user_feedback": user_feedback
    }
    return full_report


def main():
    product_url = "https://www.digikala.com/product/dkp-390759/%D8%AA%D8%B1%D8%A7%D8%B2%D9%88-%D8%A2%D8%B4%D9%BE%D8%B2%D8%AE%D8%A7%D9%86%D9%87-%D8%AF%DB%8C%D8%AC%DB%8C%D8%AA%D8%A7%D9%84%DB%8C-%D8%A7%D9%84%DA%A9%D8%AA%D8%B1%D9%88%D9%86%DB%8C%DA%A9-%D9%85%D8%AF%D9%84-sf-400-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-10-%DA%A9%DB%8C%D9%84%D9%88%DA%AF%D8%B1%D9%85/"
    
    final_report = product_details(product_url)
    
    if final_report:
        return final_report
    return None

if __name__ == "__main__":
    main()