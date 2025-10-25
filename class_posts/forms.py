from django import forms
from .models import ClassPost

class ClassPostForm(forms.ModelForm):
    class Meta:
        model = ClassPost
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(attrs={
                "placeholder": "Chia sẻ điều gì đó với lớp của bạn...",
                "rows": 3,
                "class": "form-control"
            })
        }
