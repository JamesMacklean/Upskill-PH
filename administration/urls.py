from unicodedata import name
from django.urls import path, include
from . import views


urlpatterns = [
    path('administration',views.main, name="admin-main"),
    path('administration/partners',views.partners, name="admin-partners"),
    path('administration/staff',views.staff, name="admin-staff"),
]