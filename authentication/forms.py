from dataclasses import fields
from pyexpat import model
from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = '__all__'

class EmploymentForm(forms.ModelForm):
    class Meta:
        model = Employment
        fields = '__all__'