from django.contrib import admin
from .models import LegalReference, LegalRequest, UserProfile

@admin.register(LegalReference)
class LegalReferenceAdmin(admin.ModelAdmin):
    # عرض الحقول الموجودة فعلياً في الموديل
    list_display = ('title', 'country', 'created_at')
    # الفلترة حسب الدولة
    list_filter = ('country',)
    # البحث بالعنوان والتاغات
    search_fields = ('title', 'tags')

@admin.register(LegalRequest)
class LegalRequestAdmin(admin.ModelAdmin):
    # عرض الحقول: المستخدم، الخدمة، الدولة، وتاريخ الطلب
    list_display = ('user', 'service_type', 'country', 'created_at')
    # الفلترة حسب نوع الخدمة والدولة
    list_filter = ('service_type', 'country')
    # البحث باسم المستخدم
    search_fields = ('user__username', 'details')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'firm_name', 'phone')
    search_fields = ('user__username', 'firm_name')