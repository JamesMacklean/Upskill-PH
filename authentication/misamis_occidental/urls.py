from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Add other paths specific to misamis-occidental subdomain here
]
