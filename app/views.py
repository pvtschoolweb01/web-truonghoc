from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from .forms import ProfileForm, ReportForm, AvatarForm, AnswerForm
from .models import Thoikhoabieu
from .models import Profile
from .models import MinigameAnswer
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import ReportForm
from .models import Profile
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ReportForm
from .models import Profile
# Create your views here.
def home(request):
    context = {}
    return render(request, 'app/home.html', context)

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    context = {
        'form' : form
    }
    return render(request, 'app/register.html', context)

def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)   
            return redirect('home')
        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu!')
    return render(request, 'app/login.html', context)

def logout(request):
    auth_logout(request)
    return redirect('home')

def notifi(request):
    return render(request, 'app/notifi.html', {})

def thoikhoabieu(request):
    lopdf = "10A1"
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user=request.user)
        lopdf = profile.class_name
    lop = request.GET.get("lop", lopdf)
    buoi = request.GET.get("buoi", "sang")

    tkb_records = Thoikhoabieu.objects.filter(
        lop__iexact=lop, buoi__iexact=buoi
    ).order_by("thu", "tiet")

    tkb = {}
    for rec in tkb_records:
        tkb.setdefault(str(rec.thu), {})[str(rec.tiet)] = rec.mon
    context = {
        "tkb": tkb,
        "lop": lop,
        "buoi": buoi,
    }
    return render(request, 'app/thoikhoabieu.html', context)

def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = AvatarForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = AvatarForm(instance=profile)
    context = {
        'form' : form,
        'profile' : profile
    }
    return render(request, 'app/profile.html', context)

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "app/settingprofile.html", {"form": form, "profile": profile})

def setting(request):
    context = {}
    return render(request, 'app/setting.html', context)



@login_required
def send_report(request):
    if request.method == "POST":
        profile = get_object_or_404(Profile, user=request.user)
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            attachment = form.cleaned_data.get("attachment")

            # 💌 Nội dung HTML đẹp
            html_content = f"""
            <div style="font-family:Arial, sans-serif; background:#f7f9fc; padding:20px; border-radius:10px;">
                <h2 style="color:#3366cc;">📩 Báo cáo từ người dùng</h2>
                <div style="background:white; padding:15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <p><b>Người dùng:</b> {profile.username}</p>
                    <p><b>Tên:</b> {profile.full_name}</p>
                    <p><b>Lớp:</b> {profile.class_name}</p>
                    <p><b>Email:</b> {profile.email}</p>
                    <hr style="margin:10px 0;">
                    <p><b>Tiêu đề:</b> {subject}</p>
                    <p><b>Nội dung:</b></p>
                    <div style="background:#f2f2f2; padding:10px; border-radius:6px;">{message}</div>
                </div>
            </div>
            """

            # Bản text (phòng khi không hiển thị HTML)
            text_content = (
                f"Người dùng: {profile.username}\n"
                f"Tên: {profile.full_name}\n"
                f"Lớp: {profile.class_name}\n"
                f"Email: {profile.email}\n"
                f"Tiêu đề: {subject}\n\n"
                f"Nội dung:\n{message}"
            )

            email = EmailMultiAlternatives(
                subject=f"[Báo cáo] {subject}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["pvtschoolweb01@gmail.com"],
            )
            email.attach_alternative(html_content, "text/html")

            # 📎 Nếu có file đính kèm thì gửi kèm theo
            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)

            email.send()

            return redirect("success")
    else:
        form = ReportForm()

    return render(request, "app/baocao.html", {"form": form})


def rpsuccess(request):
    return render(request, 'app/success.html')

def minigame(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để tham gia minigame!")
            return redirect("login")
        if MinigameAnswer.objects.filter(user=request.user).exists():
            messages.error(request, "Bạn đã gửi câu trả lời trước đó, không thể gửi thêm.")
            return redirect("minigame")
        answer = request.POST.get("answer", "").strip()
        if answer:
            MinigameAnswer.objects.create(user=request.user, answer=answer)
            send_mail(
                subject="Câu trả lời minigame",
                message=f"Người chơi: {request.user.username if request.user.is_authenticated else 'Khách'}\n\nCâu trả lời:\n{answer}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["prod.magegr@gmail.com"],
            )
            messages.success(request, "🎉 Câu trả lời đã được gửi thành công!")
            return redirect("minigame")
        else:
            messages.error(request, "❌ Vui lòng nhập câu trả lời trước khi gửi.")

    return render(request, "app/minigame.html")