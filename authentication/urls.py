from unicodedata import name
from django.contrib import admin
from django.urls import path,include, re_path
from . import views
from .views import SessionChecker

urlpatterns = [
    path('',views.home, name="home"),
    path('signup/',views.signup, name="signup"),
    path('signin/',views.signin, name="signin"),
    path('signout/',views.signout, name="signout"),
    path('success/<user_hash>/', views.success, name="success"),
    path('verify/<user_hash>/', views.verify_account, name="verify_account"),
    path('profile/', views.profile, name="profile"),
    path('edit/', views.edit_profile, name="edit"),
    path('account/', views.account, name="account"),
    path('sessions/', SessionChecker.as_view(), name="sessions"),
    path('application/<partner_id>/<program_id>/', views.application, name="application"),
    path('program/<partner_id>/<program_id>/', views.program, name="program"),
    path('partner/', views.partner, name="partner"),
    path('certificate/', views.certificate, name="certificate"),
    
    # path('courses/',views.courses, name="courses"),
    
    path('guidelines/',views.guidelines, name="guidelines"),
    path('privacy/', views.privacy, name="privacy")
]