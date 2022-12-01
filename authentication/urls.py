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
    path('partner', views.partner, name="partner"),
    path('sampleprogram1', views.sampleprogram1, name="sampleprogram1"),
    path('sampleprogram2', views.sampleprogram2, name="sampleprogram2"),
    path('sampleprogram3', views.sampleprogram3, name="sampleprogram3"),
    path('sampleprogram4', views.sampleprogram4, name="sampleprogram4"),
    path('sampleprogram5', views.sampleprogram5, name="sampleprogram5"),
    path('certificate', views.certificate, name="certificate")
]