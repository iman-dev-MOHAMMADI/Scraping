import requests
import json
import logging
from typing import Dict, Any, List

# تنظیمات لاگ‌گیری برای نمایش بهتر خطاها و اطلاعات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_digikala(query: str, page: int = 1, filters: Dict[str, Any] = None):
    """
    محصولات را بر اساس یک عبارت و فیلترهای مشخص در سایت دیجی‌کالا جستجو می‌کند.

    Args:
        query (str): عبارت مورد نظر برای جستجو (مثلاً 'ماشین').
        page (int): شماره صفحه نتایج. پیش‌فرض 1 است.
        filters (dict, optional): دیکشنری شامل فیلترهای جستجو. مثال:
            {
                'price': {'min': 500000, 'max': 2000000}, # قیمت بین ۵۰۰ هزار تا ۲ میلیون تومان
                'has_selling_stock': True,                  # فقط کالاهای موجود
                'brands': [36599, 4841],                     # فیلتر بر اساس ID برند
                'seller_types': ['digikala']                # فقط کالاهای فروشنده دیجی‌کالا
            }

    Returns:
        list: لیستی از دیکشنری‌ها که هر کدام اطلاعات یک محصول را شامل می‌شود.
              در صورت بروز خطا یا عدم وجود نتیجه، لیست خالی برمی‌گرداند.
    """
    
    api_url = "https://api.digikala.com/v1/search/"

    # پارامترهای پایه
    params = {
        'q': query,
        'page': page,
    }

    # اضافه کردن فیلترها به پارامترهای درخواست
    if filters:
        logging.info(f"اعمال فیلترهای زیر: {filters}")
        for key, value in filters.items():
            # فیلتر قیمت
            if key == 'price' and isinstance(value, dict):
                if 'min' in value:
                    params['price[min]'] = value['min']
                if 'max' in value:
                    params['price[max]'] = value['max']
            # فیلترهای سوییچ (boolean)
            elif isinstance(value, bool) and value:
                # API دیجی‌کالا معمولاً برای مقادیر True از '1' استفاده می‌کند
                params[key] = 1
            # فیلترهای لیستی (مانند برندها یا نوع فروشنده)
            elif isinstance(value, list):
                # فرمت پارامتر برای لیست: brands[0]=123&brands[1]=456
                for i, item_id in enumerate(value):
                    params[f'{key}[{i}]'] = item_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    logging.info(f"در حال ارسال درخواست برای جستجوی '{query}' در صفحه {page}...")
    
    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"خطا در برقراری ارتباط با سرور دیجی‌کالا: {e}")
        return []

    data = response.json()

    if not data.get('data') or not data['data'].get('products'):
        logging.warning("هیچ محصولی برای این جستجو و فیلترها یافت نشد.")
        return []

    products_list = data['data']['products']
    cleaned_products = []
    
    logging.info(f"تعداد {len(products_list)} محصول یافت شد. در حال پردازش اطلاعات...")

    for product in products_list:
        default_variant = product.get('default_variant', {})
        price_info = default_variant.get('price', {})
        seller_info = default_variant.get('seller', {})
        rating_info = product.get('rating', {})
        
        product_uri = product.get('url', {}).get('uri', '')
        product_url = f"https://www.digikala.com{product_uri}" if product_uri else "لینک ناموجود"

        cleaned_product_data = {
            'id': product.get('id'),
            'title_fa': product.get('title_fa', 'بدون عنوان'),
            'status': product.get('status', 'نامشخص'),
            'image_url': product.get('images', {}).get('main', {}).get('url', [None])[0],
            'product_page_url': product_url,
            'price': {
                'selling_price': price_info.get('selling_price', 0),
                'rrp_price': price_info.get('rrp_price', 0),
                'discount_percent': price_info.get('discount_percent', 0),
            },
            'rating': {
                'rate': rating_info.get('rate', 0),
                'count': rating_info.get('count', 0),
            },
            'seller': {
                'name': seller_info.get('title', 'نامشخص'),
                'url': seller_info.get('url', 'لینک ناموجود')
            },
            'digiclub_points': default_variant.get('digiclub', {}).get('point', 0)
        }
        cleaned_products.append(cleaned_product_data)

    return cleaned_products



# Start-------------------------------------------------------------------------------------------
if __name__ == "__main__":
    SEARCH_QUERY = "ماشین کنترلی"
    PAGE_NUMBER = 1
    OUTPUT_FILENAME = "digikala_filtered_results.json"


    #Filter_Search
    filter_options = {
        'price': {
            'min': 1000000,   # حداقل قیمت: ۱ میلیون تومان
            'max': 5000000    # حداکثر قیمت: ۵ میلیون تومان
        },
        'has_selling_stock': True,  # فقط کالاهای موجود
        'has_jet_delivery': False,   # ارسال فوری مهم نیست
        'brands': [36599, 21824]     # فقط برندهای '20 تویز' و 'آکسفورد'
    }


    #Use_Function
    results = search_digikala(
        query=SEARCH_QUERY, 
        page=PAGE_NUMBER, 
        filters=filter_options
    )

    if results:
        try:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            logging.info(f"نتایج فیلترشده با موفقیت در فایل '{OUTPUT_FILENAME}' ذخیره شد.")
        except IOError as e:
            logging.error(f"خطا در نوشتن فایل: {e}")
    else:
        logging.warning("هیچ نتیجه‌ای برای ذخیره‌سازی وجود ندارد.")