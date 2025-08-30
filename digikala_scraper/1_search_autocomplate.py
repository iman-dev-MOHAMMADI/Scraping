import requests
import json

def get_digikala_autocomplete_info(search_term: str) -> dict:
    """
    اطلاعات تکمیل خودکار (autocomplete) را برای یک عبارت از API دیجی‌کالا دریافت می‌کند.

    این تابع جزئیاتی شامل پیشنهادها، دسته‌بندی‌ها، لینک‌های پیشرفته و فراداده را 
    از پاسخ API استخراج کرده و در یک ساختار منظم برمی‌گرداند.
    (بخش ترندها از این نسخه حذف شده است)

    Args:
        search_term (str): کلمه یا عبارتی که می‌خواهید جستجو کنید.

    Returns:
        dict: دیکشنری جامع حاوی اطلاعات استخراج شده.
              در صورت بروز خطا، یک دیکشنری با کلید 'error' برمی‌گرداند.
    """
    api_url = 'https://api.digikala.com/v1/autocomplete/'
    base_url = 'https://www.digikala.com'
    params = {'q': search_term}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json().get('data', {})
        if not data:
            return {"error": "هیچ داده‌ای در پاسخ API یافت نشد."}

        # 1. استخراج پیشنهادهای تکمیل خودکار
        suggestions = list(set([
            item.get('keyword')
            for item in data.get('auto_complete', []) if item.get('keyword')
        ]))

        # 2. استخراج دسته‌بندی‌ها با جزئیات کامل
        categories = [
            {
                "keyword": item.get('keyword'),
                "category_id": item.get('category', {}).get('id'),
                "category_title_fa": item.get('category', {}).get('title_fa'),
                "category_title_en": item.get('category', {}).get('title_en'),
                "category_code": item.get('category', {}).get('code')
            }
            for item in data.get('categories', [])
        ]

        # 3. استخراج لینک‌های پیشرفته (Advanced Links) با جزئیات و لینک کامل
        advanced_links = [
            {
                "keyword": item.get('keyword'),
                "category_id": item.get('category', {}).get('id'),
                "category_title_fa": item.get('category', {}).get('title_fa'),
                "category_code": item.get('category', {}).get('code'),
                "url": base_url + item.get('category', {}).get('url', {}).get('uri', '')
            }
            for item in data.get('advance_links', [])
        ]

        # 4. استخراج فراداده (Metadata)
        metadata = {
            "search_version": data.get('search_version'),
            "trending_version": data.get('trending_version'),
            "is_text_lenz_eligible": data.get('is_text_lenz_eligible')
        }

        # برگرداندن نتیجه نهایی بدون کلید 'trends'
        return {
            "query": search_term,
            "suggestions": suggestions,
            "categories": categories,
            "advanced_links": advanced_links,
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"خطا در ارسال درخواست: {e}"}
    except json.JSONDecodeError:
        return {"error": "پاسخ دریافتی فرمت JSON معتبر ندارد."}


# --- مثال کاربردی برای تست تابع ---
if __name__ == "__main__":
    query = 'لپ تاپ'
    
    # فراخوانی تابع
    autocomplete_data = get_digikala_autocomplete_info(query)

    # Return the result for LLM consumption
    return autocomplete_data