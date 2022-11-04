from unicodedata import name
from django.urls import path, include
from . import views


urlpatterns = [
    path('administration',views.main, name="admin-main"),
    path('administration/partner',views.partner, name="admin-partner"),
    path('administration/staff',views.staff, name="admin-staff"),
]