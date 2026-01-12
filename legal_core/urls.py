from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('signup/', views.signup, name='signup'),

    # استخدام نظام Django الجاهز للدخول مع تحديد قالبنا الخاص
    path('login/', auth_views.LoginView.as_view(template_name='legal_core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('order/audit/', views.order_service, {'service_type': 'audit'}, name='audit_order'),
    path('order/engineer/', views.order_service, {'service_type': 'engineer'}, name='engineer_order'),
    path('order/protect/', views.order_service, {'service_type': 'protect'}, name='protect_order'),
    path('library/', views.legal_library, name='legal_library'),
    path('compare/', views.compare_laws, name='compare_laws'),
    path('export-pdf/<int:law1_id>/<int:law2_id>/', views.export_comparison_pdf, name='export_pdf'),
    path('library/chat/', views.library_chatbot, name='library_chatbot'),
    path('library/stats/', views.library_stats, name='library_stats'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('search/', views.legal_search, name='legal_search'),
    path('analyze/<int:law_id>/', views.ai_legal_engineer, name='ai_analyze'),
    path('export-ai/<int:law_id>/', views.export_ai_report_pdf, name='export_ai_report'),
]