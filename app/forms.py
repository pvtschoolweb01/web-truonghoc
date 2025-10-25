from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(format="%d/%m/%Y", attrs={"type": "date"}),
        input_formats=["%d/%m/%Y", "%Y-%m-%d"]
    )
    class Meta:
        model = Profile
        fields = ["full_name", "birth_date", "class_name", "email", "phone", "typeuser", "sex", "avatar"]

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
     
from django import forms

class ReportForm(forms.Form):
    subject = forms.CharField(label="Tiêu đề", max_length=200)
    message = forms.CharField(label="Nội dung", widget=forms.Textarea)
    attachment = forms.FileField(label="Tệp đính kèm", required=False)

    
class AnswerForm(forms.Form):
    answer = forms.CharField(
        label="Câu trả lời của bạn",
        max_length=500,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Nhập câu trả lời minigame...",
            "rows": 3
        })
    )
