from django.urls import path, include
from . import views

urlpatterns = [
    path('class_feed/<str:class_name>/', views.class_feed, name='class_feed'),
    path('review/', views.review_posts, name='review_posts'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('approve/<int:post_id>/', views.approve_post, name='approve_post'),
    path('delete_admin/<int:post_id>/', views.delete_post_admin, name='delete_post_admin'),
]

