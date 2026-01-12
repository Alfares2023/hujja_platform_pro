from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import LegalRequest


@receiver(post_save, sender=LegalRequest)
def send_status_update_email(sender, instance, created, **kwargs):
    # لا نرسل إيميل عند إنشاء الطلب لأول مرة (اختياري) بل عند التحديث
    if not created:
        subject = f"تحديث بخصوص طلبك رقم #{instance.id} - منصة حُجَّة"
        message = ""

        if instance.status == 'awaiting_deposit':
            message = f"عزيزي {instance.user.username}،\n\nتمت مراجعة طلبك أولياً. يرجى سداد رسوم الجدية (10$) لنبدأ المعالجة الذكية.\nرابط السداد: https://hujja.com/pay/{instance.id}\n\nشكراً لثقتك."

        elif instance.status == 'completed':
            message = f"تهانينا {instance.user.username}،\n\nاكتملت المعالجة القانونية لطلبك. يمكنك الآن الدخول للمنصة وتحميل الوثيقة النهائية.\n\nمنصة حُجَّة."

        if message:
            send_mail(
                subject,
                message,
                None,  # سيستخدم DEFAULT_FROM_EMAIL تلقائياً
                [instance.user.email],
                fail_silently=False,
            )