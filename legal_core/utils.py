import openai
import pdfplumber
import os
from django.conf import settings


def extract_text_from_pdf(file_path):
    """
    استخراج النص من ملفات PDF بدقة عالية
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None
    return text


def analyze_document_with_ai(order):
    """
    محرك حُجَّة العالمي: تحليل الوثيقة والتدليل بالمصادر القانونية
    """
    # 1. إعداد المفتاح (تأكد من وضعه في settings.py أو كمتغير بيئة)
    openai.api_key = getattr(settings, "OPENAI_API_KEY", "YOUR_API_KEY_HERE")

    # 2. استخراج النص من الملف المرفوع
    contract_text = extract_text_from_pdf(order.contract_file.path)

    if not contract_text:
        return "فشل النظام في قراءة محتوى الملف. يرجى التأكد من جودة الـ PDF."

    # 3. بناء "برومبت" هندسي متخصص (Prompt Engineering)
    # نركز هنا على الدولة والمصادر كما طلبت
    system_instruction = f"""
    أنت مستشار قانوني دولي وخبير في هندسة الصياغة التعاقدية.
    مهمتك هي تحليل العقود بناءً على نظام القانون في دولة ({order.country}).

    يجب أن يتضمن تحليلك ما يلي:
    1. الثغرات: حدد البنود الضعيفة أو التي تشكل خطراً على العميل.
    2. التعديل الهندسي: قدم نصاً بديلاً صريحاً للصياغة.
    3. التدليل القانوني (Critical): اذكر اسم النظام (القانون)، رقم المادة، ونصها (إن أمكن) لتدعيم وجهة نظرك.
    4. إذا كان العقد يتطلب معايير دولية (مثل UNIDROIT أو CISG)، فقم بدمجها في التحليل.

    اجعل لغتك مهنية، رصينة، وجاهزة للمراجعة من قبل خبير بشري.
    """

    user_input = f"""
    نوع المهمة: {order.get_service_type_display()}
    مجال العقد: {order.get_contract_field_display()}
    عدد الأطراف: {order.parties_count}
    الدولة المستهدفة: {order.country}

    نص العقد المستخرج:
    ---
    {contract_text[:4000]}  # إرسال أول 4000 حرف لضمان عدم تجاوز حدود الـ Token
    ---
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # نستخدم 4o لقدرته العالية على البحث والتدقيق القانوني
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,  # درجة منخفضة لضمان الدقة وعدم "التأليف"
        )

        analysis_result = response.choices[0].message.content

        # 4. حفظ النتائج في قاعدة البيانات
        order.extracted_text = contract_text
        order.ai_analysis = analysis_result
        order.status = 'UNDER_REVIEW'  # تحويل الحالة لمراجعة الخبير البشري
        order.save()

        return analysis_result

    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بمحرك الذكاء الاصطناعي: {str(e)}"