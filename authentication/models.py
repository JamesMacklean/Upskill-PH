from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ScholarProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=200, null=True)
    middle_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(null=True, blank=True)
    
    emp_status = models.CharField(max_length=200, null=True)
    industry = models.CharField(max_length=200, null=True)
    employer = models.CharField(max_length=200, null=True)
    occupation = models.CharField(max_length=200, null=True)
    exp_level = models.CharField(max_length=200, null=True)
    degree = models.CharField(max_length=200, null=True)
    university = models.CharField(max_length=200, null=True)
    field = models.CharField(max_length=200, null=True)

    bio = models.CharField(max_length=500, null=True)
    country = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=200, null=True)
    province = models.CharField(max_length=200, null=True)
    municipality = models.CharField(max_length=200, null=True)

    social = models.CharField(max_length=200, null=True)

    birthday = models.DateTimeField(null=True)

    phone = models.IntegerField(null=True)
    details_privacy = models.CharField(max_length=200, null=True)
    class Meta:
        # ordering = ['order']
        verbose_name_plural = "Scholar Profiles"
