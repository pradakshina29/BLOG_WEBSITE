from django.urls import path
from .views import post_list, post_detail, post_create, post_update, post_delete, register

urlpatterns = [
    path('', post_list, name='post_list'),
    path('register/', register, name='register'),
    path('post/new/', post_create, name='post_create'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', post_update, name='post_update'),
    path('post/<slug:slug>/delete/', post_delete, name='post_delete'),
]