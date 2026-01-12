from django.db import models
from django.contrib.auth.models import User

# 1. نموذج المراجع القانونية (المكتبة)
class LegalReference(models.Model):
    COUNTRY_CHOICES = [
        ('SA', 'السعودية'),
        ('EG', 'مصر'),
        ('AE', 'الإمارات'),
    ]
    title = models.CharField(max_length=200)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='laws/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 2. نموذج طلبات التدقيق والتحليل
class LegalRequest(models.Model):
    SERVICE_TYPES = [
        ('audit', 'تدقيق العقود'),
        ('engineer', 'هندسة العقود'),
        ('protect', 'الحماية القانونية'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    document = models.FileField(upload_to='documents/')
    country = models.CharField(max_length=50, default='SA')
    details = models.TextField(blank=True, null=True, verbose_name="تفاصيل الطلب")
    ai_report = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب {self.service_type} - {self.user.username}"

# 3. نموذج الملف الشخصي للمحامي
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firm_name = models.CharField(max_length=100, blank=True, verbose_name="اسم المكتب")
    firm_logo = models.ImageField(upload_to='firm_logos/', blank=True, null=True, verbose_name="شعار المكتب")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")

    def __str__(self):
        return f"بروفايل: {self.user.username}"