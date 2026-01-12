import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# تهيئة بيئة Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hujja_platform.settings')
django.setup()

from legal_core.models import LegalReference
from django.core.files.base import ContentFile


def explore_and_import_pdfs(target_url, country, tags):
    print(f"🔍 جاري البحث عن قوانين في: {target_url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. البحث عن كل الروابط في الصفحة
        all_links = soup.find_all('a', href=True)
        pdf_links = set()  # استخدمنا set لتجنب التكرار

        print(f"🔎 تم العثور على {len(all_links)} رابط، جاري فحص الروابط التي تحتوي على ملفات...")

        for link in all_links:
            href = link['href']
            full_url = urljoin(target_url, href)

            # إذا كان الرابط يؤدي لملف PDF مباشرة
            if full_url.lower().endswith('.pdf'):
                pdf_links.add((full_url, link.text.strip()))

            # ميزة إضافية: إذا كان الرابط يحتوي على كلمة "download" أو "view"
            # سنقوم بزيارته سريعاً للبحث عن PDF بداخله (اختياري لزيادة الدقة)

        pdf_count = 0
        for pdf_url, title in pdf_links:
            if not title: title = f"قانون مصري {pdf_count + 1}"

            print(f"📥 جاري تحميل وحفظ: {title}...")
            try:
                pdf_res = requests.get(pdf_url, headers=headers, timeout=10)
                if pdf_res.status_code == 200:
                    ref = LegalReference(
                        title=title,
                        country=country,
                        ref_type='law',
                        tags=tags,
                        source_url=pdf_url
                    )
                    file_name = f"law_{int(time.time())}_{pdf_count}.pdf"
                    ref.attachment.save(file_name, ContentFile(pdf_res.content), save=True)
                    pdf_count += 1
            except:
                print(f"⚠️ فشل تحميل الملف: {pdf_url}")

        if pdf_count == 0:
            print(
                "\n💡 نصيحة: بعض المواقع تخفي الـ PDF خلف أزرار تحميل. جرب روابط مباشرة أكثر أو ارفع الملفات يدوياً في لوحة الإدارة.")
        else:
            print(f"\n✨ تم بنجاح إضافة {pdf_count} مرجع جديد لمكتبتك!")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")


if __name__ == "__main__":
    url_to_scan = input("أدخل رابط الصفحة: ")
    user_country = input("أدخل الدولة: ")
    explore_and_import_pdfs(url_to_scan, user_country, "استيراد_ذكي")