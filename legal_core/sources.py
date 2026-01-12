# legal_core/sources.py

"""
دليل المصادر الموثوقة لمنصة حُجَّة القانونية
تم تصنيف المصادر حسب الدولة والأولوية لضمان دقة محرك الذكاء الاصطناعي.
"""

LEGAL_SOURCES = {
    'SAUDI_ARABIA': {
        'priority_1': [
            {'name': 'المركز الوطني للوثائق والمحفوظات', 'url': 'https://laws.boe.gov.sa/', 'category': 'الأنظمة الأساسية'},
            {'name': 'هيئة الخبراء بمجلس الوزراء', 'url': 'https://www.boe.gov.sa/', 'category': 'اللوائح التنفيذية'},
        ],
        'specialized': [
            {'name': 'منصة قوى (وزارة العمل)', 'url': 'https://qiwa.sa/ar/labor-law', 'category': 'قوانين العمل'},
            {'name': 'الهيئة السعودية للملكية الفكرية', 'url': 'https://www.saip.gov.sa/', 'category': 'الملكية الفكرية'},
            {'name': 'نظام المعاملات المدنية الجديد', 'url': 'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/648a8c4b-7a54-4c4c-8f1d-b01600a7b4f5/1', 'category': 'القانون المدني'},
        ]
    },
    'EGYPT': {
        'priority_1': [
            {'name': 'بوابة التشريعات المصرية (محكمة النقض)', 'url': 'http://www.cc.gov.eg/', 'category': 'الدستور والقوانين'},
            {'name': 'منصة منشورات قانونية', 'url': 'https://manshurat.org/', 'category': 'الأرشيف القانوني المفتوح'},
        ],
        'specialized': [
            {'name': 'الهيئة العامة للاستثمار (GAFI)', 'url': 'https://www.gafi.gov.eg/Arabic/Pages/default.aspx', 'category': 'قوانين الشركات'},
            {'name': 'بوابة مجلس النواب', 'url': 'http://www.parliament.gov.eg/', 'category': 'مسودات القوانين'},
        ]
    },
    'UAE': {
        'priority_1': [
            {'name': 'بوابة التشريعات الاتحادية', 'url': 'https://elaws.moj.gov.ae/', 'category': 'التشريعات الاتحادية'},
            {'name': 'البوابة الرسمية لحكومة الإمارات', 'url': 'https://u.ae/ar-ae/about-the-uae/uae-laws-and-regulations', 'category': 'دليل الأنظمة'},
        ],
        'specialized': [
            {'name': 'تشريعات دبي (DLP)', 'url': 'https://dlp.dubai.gov.ae/', 'category': 'قوانين محلية'},
            {'name': 'وزارة الموارد البشرية والتوطين', 'url': 'https://www.mohre.gov.ae/', 'category': 'قوانين العمل'},
        ]
    },
    'INTERNATIONAL': [
        {'name': 'شبكة المعلومات القانونية العربية', 'url': 'http://arablegalportal.org/', 'category': 'مقارنات عربية'},
        {'name': 'منظمة العمل الدولية (NATLEX)', 'url': 'https://www.ilo.org/dyn/natlex/', 'category': 'معايير العمل الدولية'},
    ]
}

# توجيهات للمصنف التلقائي (Auto-Classifier Tags)
LAW_TAGS = [
    'تجاري', 'مدني', 'عقاري', 'عمل', 'جنائي', 'شركات',
    'إثبات', 'إجراءات مرافعات', 'ملكية فكرية', 'إقامة واستثمار'
]