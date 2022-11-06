from unicodedata import name
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('signup',views.signup, name="signup"),
    path('signin',views.signin, name="signin"),
    path('signout',views.signout, name="signout"),
    path('success', views.success, name="success"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('profile', views.profile, name="profile"),
    path('profile/edit', views.edit_profile, name="edit")
]