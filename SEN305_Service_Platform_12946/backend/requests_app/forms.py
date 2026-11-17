from django import forms
from django.contrib.auth import get_user_model
from .models import Category, Comment, ServiceRequest
User = get_user_model()

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ("category", "title", "description", "location", "priority")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 3:
            raise forms.ValidationError("Enter at least 3 characters.")
        return body

class AssignmentForm(forms.Form):
    technician = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True, is_staff=True))

class ResolutionForm(forms.Form):
    work_notes = forms.CharField(widget=forms.Textarea, min_length=3)
    resolution_summary = forms.CharField(widget=forms.Textarea, min_length=3)
