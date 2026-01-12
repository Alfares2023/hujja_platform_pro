import PyPDF2
import time
import openai
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .sources import LAW_TAGS
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Count
from .models import LegalRequest, LegalReference
from .forms import LegalRequestForm, LegalUploadForm
from django.http import JsonResponse
from .models import UserProfile
from .forms import UserProfileForm

# --- 1. دالة استخراج النص من PDF ---
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for i in range(min(len(reader.pages), 10)):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        text = f"خطأ في قراءة الملف: {str(e)}"
    return text
def about_us(request):
    return render(request, 'legal_core/about.html')


# --- 2. محرك الذكاء الاصطناعي ---
def get_mock_ai_analysis(extracted_text, service_type, country):
    time.sleep(1)
    words = [w for w in extracted_text.split() if len(w) > 4][:10]
    search_query = Q()
    for word in words:
        search_query |= Q(content__icontains=word) | Q(title__icontains=word)

    related_refs = LegalReference.objects.filter(search_query, country=country).distinct()[:2]
    reference_info = ""
    if related_refs.exists():
        reference_info = "\n\n📋 **المصادر القانونية:**\n"
        for ref in related_refs:
            reference_info += f"- تم الاستناد إلى: {ref.title}\n"
    else:
        reference_info = "\n\n⚠️ (ملاحظة: لم يتم العثور على نصوص متطابقة مباشرة)."

    analysis_base = {
        'audit': "✅ تم تدقيق الوثيقة وتحديد الثغرات.",
        'engineer': "🛠️ تم تحليل هيكل العقد.",
        'protect': "🛡️ تم فحص البنود للوقاية."
    }
    return analysis_base.get(service_type, "تمت المعالجة.") + reference_info


# --- 3. صفحات الواجهة العامة والمكتبة ---
def home(request):
    return render(request, 'legal_core/home.html')


@login_required
def legal_library(request):
    if request.method == 'POST':
        form = LegalUploadForm(request.POST, request.FILES)
        if form.is_valid():
            law = form.save()

            # استخراج النص وتصنيفه آلياً في الخلفية
            if law.attachment:
                raw_text = extract_text_from_pdf(law.attachment)
                law.content = raw_text
                # تحديث الوسوم تلقائياً إذا كانت فارغة
                if not law.tags:
                    law.tags = suggest_law_tags(raw_text)
                law.save()

            messages.success(request, f"تم الرفع بنجاح وتصنيف القانون كـ: {law.tags}")
            return redirect('legal_library')
# --- 4. محرك المقارنة التفاعلي (المحدث) ---
@login_required
def compare_laws(request):
    references = LegalReference.objects.all()
    answer = None
    law1 = None
    law2 = None

    if request.method == 'POST':
        law1_id = request.POST.get('law1')
        law2_id = request.POST.get('law2')
        user_question = request.POST.get('question')

        law1 = get_object_or_404(LegalReference, id=law1_id)
        law2 = get_object_or_404(LegalReference, id=law2_id)

        # منطق البحث التفاعلي في النصوص
        def find_relevant_text(content, question):
            keywords = [k for k in question.split() if len(k) > 3]
            for paragraph in content.split('\n'):
                if any(word.lower() in paragraph.lower() for word in keywords):
                    return paragraph
            return "لم يتم العثور على نص مباشر يتعلق بهذا السؤال في هذا المرجع."

        answer = {
            'question': user_question,
            'law1_answer': find_relevant_text(law1.content, user_question),
            'law2_answer': find_relevant_text(law2.content, user_question),
            'ai_opinion': f"بناءً على مقارنة التشريعين، يظهر أن {law1.country} تتعامل مع هذا البند بتركيز إجرائي، بينما يميل التشريع في {law2.country} إلى الحماية الموضوعية."
        }

    return render(request, 'legal_core/compare.html', {
        'references': references,
        'answer': answer,
        'law1': law1,
        'law2': law2
    })


# --- 5. وظيفة تصدير التقرير إلى PDF ---
@login_required
def export_comparison_pdf(request, law1_id, law2_id):
    # جلب القوانين
    law1 = get_object_or_404(LegalReference, id=law1_id)
    law2 = get_object_or_404(LegalReference, id=law2_id)

    # الحصول على سؤال المستخدم (إذا كان موجوداً في الرابط)
    question = request.GET.get('q', 'مقارنة نصوص عامة')

    # تجهيز البيانات للقالب
    context = {
        'law1': law1,
        'law2': law2,
        'question': question,
        'date': datetime.now()
    }
        # نأخذ أول 1500 حرف فقط حتى لا يطول التقرير جداً في النسخة التجريبية
    # جلب بروفايل المستخدم
    try:
        user_profile = request.user.profile
        # نستخدم طلب.build_absolute_uri لضمان ظهور الصورة في الـ PDF بشكل صحيح
        if user_profile.firm_logo:
            logo_url = request.build_absolute_uri(user_profile.firm_logo.url)
            firm_name = user_profile.firm_name
        else:
            # شعار افتراضي في حال لم يرفع المستخدم شعاره
            logo_url = "https://cdn-icons-png.flaticon.com/512/3222/3222642.png"
            firm_name = "منصة حُجَّة للذكاء القانوني"
    except UserProfile.DoesNotExist:
        logo_url = "https://cdn-icons-png.flaticon.com/512/3222/3222642.png"
        firm_name = "منصة حُجَّة"

    context = {
        'law1': law1,
        'law2': law2,
        'question': question,
        'date': datetime.now(),
        'content1': law1.content[:1500] + "...",
        'content2': law2.content[:1500] + "...",

        # المتغيرات الجديدة للهوية
        'logo_url': logo_url,
        'firm_name': firm_name,
    }

    template = get_template('legal_core/pdf_report.html')
    html = template.render(context)
    result = BytesIO()

    # ملاحظة: دعم اللغة العربية في xhtml2pdf يتطلب إعدادات خطوط خاصة
    # لكن هذا الكود سيعمل بشكل جيد مع الحروف الإنجليزية والأرقام،
    # وقد تظهر العربية بشكل جيد إذا كان السيرفر يدعم الخطوط الافتراضية.
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        # اسم الملف وتاريخه
        filename = f"Hujja_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("حدث خطأ أثناء إنشاء ملف الـ PDF", status=400)
# --- 6. نظام الحسابات والخدمات (كما هي) ---
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    return render(request, 'legal_core/signup.html', {'form': UserCreationForm()})


@login_required
def order_service(request, service_type):
    requests_list = LegalRequest.objects.filter(user=request.user, service_type=service_type).order_by('-created_at')
    if request.method == 'POST':
        form = LegalRequestForm(request.POST, request.FILES)
        if form.is_valid():
            legal_req = form.save(commit=False)
            legal_req.user, legal_req.service_type = request.user, service_type
            legal_req.save()
            if legal_req.document:
                raw_text = extract_text_from_pdf(legal_req.document)
                legal_req.ai_report = get_mock_ai_analysis(raw_text, service_type, legal_req.country)
                legal_req.save()
            return redirect(request.path)
    return render(request, 'legal_core/order_form.html',
                  {'form': LegalRequestForm(), 'requests': requests_list, 'service_type': service_type})


@login_required
def user_dashboard(request):
    # جلب كافة الطلبات التي قدمها المستخدم
    all_requests = LegalRequest.objects.filter(user=request.user).order_by('-created_at')

    # إحصائيات سريعة للوحة التحكم
    stats = {
        'total': all_requests.count(),
        'completed': all_requests.exclude(ai_report='').count(),
        'pending': all_requests.filter(ai_report='').count(),
    }

    return render(request, 'legal_core/dashboard.html', {
        'requests': all_requests,
        'stats': stats
    })


def suggest_law_tags(extracted_text):
    """
    تقوم بفحص النص المستخرج واقتراح الوسوم المناسبة تلقائياً
    """
    suggested = []
    text_sample = extracted_text[:2000].lower()  # فحص بداية القانون فقط لسرعة الأداء

    # خريطة الكلمات المفتاحية للتصنيف
    keywords_map = {
        'عمل': ['عامل', 'صاحب عمل', 'أجور', 'استقالة', 'مكافأة'],
        'تجاري': ['شركة', 'سجل تجاري', 'أسهم', 'إفلاس', 'تجارة'],
        'عقاري': ['إيجار', 'عقار', 'تسجيل عيني', 'بناء', 'أراضي'],
        'جنائي': ['عقوبة', 'حبس', 'جريمة', 'نيابة', 'تحقيق'],
        'مدني': ['التزام', 'عقد', 'تعويض', 'مسؤولية تقصيرية'],
    }

    for tag, keys in keywords_map.items():
        if any(key in text_sample for key in keys):
            suggested.append(tag)

    return ", ".join(suggested) if suggested else "عام"


@login_required
def library_stats(request):
    # 1. إحصائيات حسب الدولة
    country_stats = LegalReference.objects.values('country').annotate(total=Count('id')).order_by('-total')

    # 2. إحصائيات حسب التصنيف (Tags)
    # ملاحظة: سنقوم بتحليل الوسوم المخزنة
    tag_counts = {}
    all_tags = LegalReference.objects.values_list('tags', flat=True)
    for tags in all_tags:
        if tags:
            for tag in tags.split(','):
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 3. حساب نسبة الاكتمال (الملفات التي تم استخراج نصوصها بنجاح)
    total_refs = LegalReference.objects.count()
    processed_refs = LegalReference.objects.exclude(content='').count()
    processing_rate = (processed_refs / total_refs * 100) if total_refs > 0 else 0

    return render(request, 'legal_core/stats.html', {
        'country_stats': country_stats,
        'tag_stats': tag_counts,
        'total_refs': total_refs,
        'processing_rate': processing_rate,
    })


def library_chatbot(request):
    user_message = request.GET.get('message', '').strip()

    if not user_message:
        return JsonResponse({'reply': 'كيف يمكنني مساعدتك في مكتبة حُجَّة اليوم؟'})

    # البحث في المراجع بناءً على رسالة المستخدم (العنوان، المحتوى، أو الوسوم)
    results = LegalReference.objects.filter(
        Q(title__icontains=user_message) |
        Q(tags__icontains=user_message) |
        Q(content__icontains=user_message)
    ).distinct()[:3]

    if results.exists():
        reply = "وجد حُجَّة لك هذه المراجع قد تفيدك:<br><ul class='list-unstyled mt-2'>"
        for ref in results:
            # نتحقق من وجود ملف قبل وضع الرابط
            file_url = ref.attachment.url if ref.attachment else "#"
            reply += f"<li><i class='fas fa-file-pdf text-danger'></i> <a href='{file_url}' target='_blank'>{ref.title} ({ref.country})</a></li>"
        reply += "</ul>"
    else:
        reply = "عذراً، لم أجد نتائج مباشرة في المكتبة لهذه الكلمات. هل تقصد موضوعاً يتعلق بـ (العمل) أو (العقارات)؟"

    return JsonResponse({'reply': reply})
@login_required
def profile_settings(request):
    # التأكد من وجود بروفايل للمستخدم، أو إنشاؤه إذا لم يوجد
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث شعار وبيانات المكتب بنجاح!")
            return redirect('profile_settings')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'legal_core/profile.html', {'form': form})


def legal_search(request):
    query = request.GET.get('q', '')  # جلب الكلمة المكتوبة في خانة البحث
    results = []

    if query:
        # البحث في العنوان، المحتوى، والتاغات (Tags)
        # icontains تعني بحث غير حساس لحالة الأحرف (مناسب جداً للعربية)
        results = LegalReference.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        ).distinct()

    return render(request, 'legal_core/search_results.html', {
        'results': results,
        'query': query,
        'count': results.count() if results else 0
    })


def ai_legal_engineer(request, law_id):
    law = get_object_or_404(LegalReference, id=law_id)

    # تحديد "البرومبت" (الأمر الموجه للذكاء الاصطناعي)
    # نحن هنا لا نطلب منه مجرد تلخيص، بل "هندسة" النص
    prompt = f"""
    أنت مستشار قانوني خبير. أمامك النص القانوني التالي:
    "{law.content[:2000]}"

    المطلوب منك:
    1. تبسيط النص ليكون مفهوماً لشخص غير قانوني.
    2. استخراج أهم 3 حقوق وأهم 3 واجبات وردت في النص.
    3. تنبيه المحامي لأي ثغرة قانونية محتملة في هذا النص.
    اجعل الإجابة بتنسيق نقاط واضح وباللغة العربية الفصحى.
    """

    try:
        # استدعاء API (تأكد من وضع مفتاحك في إعدادات البيئة)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_analysis = response.choices[0].message.content
    except Exception as e:
        ai_analysis = f"عذراً، حدث خطأ أثناء الاتصال بمحرك الذكاء الاصطناعي: {str(e)}"

    return render(request, 'legal_core/ai_analysis.html', {
        'law': law,
        'analysis': ai_analysis
    })


@login_required
def export_ai_report_pdf(request, law_id):
    law = get_object_or_404(LegalReference, id=law_id)

    # 1. جلب بيانات البروفايل والشعار
    try:
        profile = request.user.profile
        firm_name = profile.firm_name or "منصة حُجَّة"
        logo_url = request.build_absolute_uri(profile.firm_logo.url) if profile.firm_logo else None
    except:
        firm_name = "منصة حُجَّة"
        logo_url = None

    # 2. جلب التحليل (يمكنك تخزينه في الـ Session لتوفير تكلفة الـ API أو إعادة توليده)
    # هنا سنفترض أننا نرسل النص الذي تم توليده للتو
    ai_content = request.POST.get('ai_content', 'لا يوجد محتوى للتقرير')

    context = {
        'law': law,
        'firm_name': firm_name,
        'logo_url': logo_url,
        'analysis': ai_content,
        'date': datetime.now(),
        'user': request.user
    }

    # 3. توليد الـ PDF
    template = get_template('legal_core/pdf_report_template.html')
    html = template.render(context)
    result = BytesIO()

    # تحويل HTML إلى PDF مع دعم العربية
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Legal_Report_{law.id}.pdf"'
    return response