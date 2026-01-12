from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('legal_core.urls')), # تأكد أن هذا يشير لتطبيقك
]

# هذا السطر هو المفتاح لحل مشكلة الـ 404 في روابط الميديا
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)