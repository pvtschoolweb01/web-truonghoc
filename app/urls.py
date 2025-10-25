from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('thoikhoabieu/', views.thoikhoabieu, name="thoikhoabieu"),
    path('minigame/', views.minigame, name='minigame'),
    path("report/", views.send_report, name="report"),
    path("success/", views.rpsuccess, name="success"),
    path('profile', views.profile, name='profile'),
    path('setting/', views.setting, name='setting'),
    path('setting/settingprofile/', views.profile_view, name='settingprofile'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('logoutconfirm', views.notifi, name='logoutconfirm'),
    path('class-posts/', include(('class_posts.urls', 'class_posts'), namespace='class_posts')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
