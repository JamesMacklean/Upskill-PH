from django.forms import ModelForm
from .models import *

class ScholarProfileForm(ModelForm):
    class Meta:
        model = ScholarProfile
        fields = '__all__'