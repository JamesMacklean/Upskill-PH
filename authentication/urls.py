from unicodedata import name
from django.contrib import admin
from django.urls import path,include
from . import views
from .views import SessionChecker

urlpatterns = [
    path('',views.home, name="home"),
    path('signup',views.signup, name="signup"),
    path('signin',views.signin, name="signin"),
    path('signout',views.signout, name="signout"),
    path('success', views.success, name="success"),
    path('verify/<user_hash>', views.verify_account, name="verify_account"),
    path('profile', views.profile, name="profile"),
    path('edit', views.edit_profile, name="edit"),
    path('sessions', SessionChecker.as_view(), name="sessions"),
    path('program/<slug>', views.program, name="program"),
    path('partner', views.partner, name="partner")
]