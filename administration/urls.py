from unicodedata import name
from django.urls import path, include
from . import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^administration$',views.main, name="admin-main"),
    url(r'^administration/partners$',views.partners, name="admin-partners"),
    url(r'^administration/staff$',views.staff, name="admin-staff"),
]