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
    # path('program/<partner_id>/<program_id>/', views.program, name="program"),
    path('program/<slug>/', views.program, name="program"),
    path('partner/', views.partner, name="partner"),
    path('certificate/', views.certificate, name="certificate"),
    path('partner/', views.partner, name="partner"),
    path('dashboard/', views.applied_programs, name="dashboard"),
    path('administrator/', views.admin_dashboard, name='admin_dashboard'),
    path('administrator/users/', views.user_management, name='user_management'),
    path('administrator/users/<int:user_id>/', views.user_details, name='user_details'),
    path('administrator/partner/<int:partner_id>/', views.admin_partners, name='admin_partners'),
    path('administrator/license-codes/<slug>/', views.license_codes, name='license_codes'),
    # path('courses/',views.courses, name="courses"),
    
    path('guidelines/',views.guidelines, name="guidelines"),
    path('privacy/', views.privacy, name="privacy"),
    path('contact-us/', views.contact, name="contact"),
    
    # COURSERA
    path('refresh/', views.refresh_token, name="refresh"),
]