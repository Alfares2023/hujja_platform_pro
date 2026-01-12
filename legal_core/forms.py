from django import forms
from .models import LegalRequest, LegalReference, UserProfile

class LegalRequestForm(forms.ModelForm):
    class Meta:
        model = LegalRequest
        fields = ['country', 'document', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب ملاحظاتك هنا...'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LegalUploadForm(forms.ModelForm):
    class Meta:
        model = LegalReference
        fields = ['title', 'country', 'attachment', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عمل, عقارات...'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['firm_name', 'phone', 'firm_logo']
        widgets = {
            'firm_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }