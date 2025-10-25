from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ClassPost
from .forms import ClassPostForm

# ===== Học sinh: bảng tin lớp =====
@login_required
def class_feed(request, class_name):
    # --- Lấy & xóa thông báo tạm trong session (nếu có) ---
    message = request.session.pop("temp_message", None)

    # --- Kiểm tra quyền ---
    if not request.user.is_staff and request.user.profile.class_name != class_name:
        request.session["temp_message"] = "❌ Bạn không thuộc lớp này!"
        return redirect("class_feed", class_name=request.user.profile.class_name)

    # --- Xử lý đăng bài ---
    if request.method == "POST":
        form = ClassPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.class_name = class_name
            post.is_approved = False
            post.save()
            request.session["temp_message"] = "✅ Bài đã được gửi chờ duyệt!"
            # 👉 Redirect để chặn gửi lại form khi reload
            return redirect("class_feed", class_name=class_name)
    else:
        form = ClassPostForm()

    # --- Lấy bài đã duyệt ---
    posts = ClassPost.objects.filter(
        class_name=class_name, is_approved=True
    ).order_by("-created_at")

    return render(request, "class_posts/class_feed.html", {
        "posts": posts,
        "form": form,
        "class_name": class_name,
        "message": message,
    })


# ===== Học sinh: xóa bài của chính mình =====
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ClassPost, id=post_id)

    # Kiểm tra quyền
    if post.author != request.user or request.user.profile.class_name != post.class_name:
        request.session["temp_message"] = "❌ Bạn không có quyền xóa bài này."
    else:
        post.delete()
        request.session["temp_message"] = "✅ Xóa bài thành công!"

    # 👉 Redirect về bảng tin lớp để tránh gửi lại form khi reload
    return redirect("class_feed", class_name=post.class_name)


@staff_member_required
def approve_post(request, post_id):
    post = get_object_or_404(ClassPost, id=post_id)
    post.is_approved = True
    post.save()
    request.session["temp_message"] = "✅ Bài đã được duyệt!"
    return redirect("review_posts")

@staff_member_required
def delete_post_admin(request, post_id):
    post = get_object_or_404(ClassPost, id=post_id)
    post.delete()
    request.session["temp_message"] = "❌ Bài đã bị xóa!"
    return redirect("review_posts")
@staff_member_required
def review_posts(request):
    # --- Lấy & xóa thông báo tạm trong session (nếu có) ---
    message = request.session.pop("temp_message", None)

    # --- Lấy bài chưa duyệt ---
    posts = ClassPost.objects.filter(is_approved=False).order_by("-created_at")

    return render(request, "class_posts/review_posts.html", {
        "posts": posts,
        "message": message,
    })


