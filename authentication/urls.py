from unicodedata import name
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from .views import SessionChecker

urlpatterns = [
    path('',views.home, name="home"),
    path('account/', views.account, name="account"),
    path('administrator/', views.admin_dashboard, name='admin_dashboard'),
    path('administrator/users/', views.user_management, name='user_management'),
    path('administrator/users/<int:user_id>/', views.user_details, name='user_details'),
    path('administrator/partner/<int:partner_id>/', views.admin_partners, name='admin_partners'),
    path('administrator/license-codes/<slug>/', views.license_codes, name='license_codes'),
    path('certificate/', views.certificate, name="certificate"),
    path('contact-us/', views.contact, name="contact"),
    path('dashboard/', views.applied_programs, name="dashboard"),
    path('guidelines/',views.guidelines, name="guidelines"),
    path('lakip/',views.lakip_landing, name='lakip-landing'),
    path('lakip/apply/',views.lakip_application, name='lakip-application'),
    path('partner/', views.partner, name="partner"),
    path('partner/<slug:partner_slug>', views.partner_slug, name="partner_slug"),
    path('partner/<slug:partner_slug>/edit/', views.partner_edit, name='partner_edit'),
    path('partner/<slug:partner_slug>/<slug:program_slug>/', views.program_slug, name='program_slug'),
    path('partner/<slug:partner_slug>/<slug:program_slug>/application/', views.application, name="application"),
    path('partner/<slug:partner_slug>/<slug:program_slug>/edit/', views.program_edit, name="program_edit"),
    # path('partner/<slug:program_slug>/application/', views.application, name="application"),
    
    path('privacy/', views.privacy, name="privacy"),
    path('profile/', views.profile, name="profile"),
    path('profile/edit/', views.edit_profile, name="edit"),
    path('program/<slug>/', views.program, name="program"),
    path('sessions/', SessionChecker.as_view(), name="sessions"),
    path('signout/',views.signout, name="signout"),

    # SUBDOMAIN PATHS
    path('', include('authentication.accounts.urls')),
    path('', include('authentication.misamis_occidental.urls')),
    
]