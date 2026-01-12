import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# --- إضافة هذا الجزء لحل مشكلة المسارات ---
# الحصول على المسار الحالي للمشروع
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hujja_platform.settings')
django.setup()
# ---------------------------------------

from legal_core.models import LegalReference


def fast_import_law(url, country="عام", ref_type="law"):
    print(f"جاري محاولة سحب البيانات من: {url}...")
    # ... باقي الدالة كما هي في الكود السابق ...
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').text.strip() if soup.find('h1') else "مرجع مستورد"
        paragraphs = soup.find_all('p')
        content = "\n".join([p.text.strip() for p in paragraphs if len(p.text) > 20])

        ref, created = LegalReference.objects.get_or_create(
            title=title,
            defaults={
                'content': content,
                'country': country,
                'ref_type': ref_type,
                'source_url': url,
                'tags': 'استيراد_آلي'
            }
        )
        if created:
            print(f"✅ تم بنجاح إضافة: {title}")
        else:
            print(f"ℹ️ المرجع موجود مسبقاً: {title}")
    except Exception as e:
        print(f"❌ فشل الاستيراد: {e}")


if __name__ == "__main__":
    # جرب استخدام رابط حقيقي يحتوي على نص قانوني
    # مثال لرابط من موقع (موسوعة القوانين العربية أو غيرها)
    test_url = "ضع_الرابط_هنا"
    if test_url != "ضع_الرابط_هنا":
        fast_import_law(test_url, "دولة المرجع")
    else:
        print("الرجاء وضع رابط حقيقي في متغير test_url داخل الملف.")