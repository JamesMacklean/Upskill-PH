from unicodedata import name
from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [   
    path('signin/',views.signin, name="signin"),
    path('signup/',views.signup, name="signup"),
    path('success/<user_hash>/', views.success, name="success"),
    path('verify/<user_hash>/', views.verify_account, name="verify_account"),

]