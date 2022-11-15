from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ScholarProfile(models.Model):
    user = models.OneToOneField(
            User, null=True,
            on_delete=models.CASCADE)

    fname = models.CharField(max_length=200, null=True)
    middle_name = models.CharField(max_length=200, null=True)
    lname = models.CharField(max_length=200, null=True)
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
    gender = models.CharField(max_length=200, null=True)
    birthday = models.DateTimeField(null=True)

    phone = models.IntegerField(null=True)
    details_privacy = models.CharField(max_length=200, null=True)
    class Meta:
        # ordering = ['order']
        verbose_name_plural = "Scholar Profiles"

    def __str__(self):
        return self.user.username

    @property
    def username(self):
        return self.user.username

    @property
    def first_name(self):
        try: 
            fname =  self.user.first_name
        except:
            fname = ""
        return fname

    @property
    def last_name(self):
        try: 
            lname =  self.user.last_name
        except:
            lname = ""
        return lname

# class education(models.Model):
#     id = models.AutoField(primary_key=True)
#     degree = models.CharField(max_length=2,null=True)
#     school = models.CharField(max_length=200,null=True)
#     study = models.CharField(max_length=200, null=True)
#     last_modified = models.DateTimeField(null=True)
#     user_id = #EDIT. ADD FOREIGN RELATION

# class employment(models.Model):
#     id = models.AutoField(primary_key=True)
#     employ_status = models.CharField(max_length=255, null=True)
#     industry = models.CharField(max_length=255, null=True)
#     employer = models.CharField(max_length=255, null=True)
#     occupation = models.CharField(max_length=255, null=True)
#     experience = models.CharField(max_length=255, null=True)
#     last_modified = models.DateTimeField(null=True)
#     user_id = #EDIT. ADD RELATION TO OTHER TABLE


# class partner(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_field=255, null=True)

# class parter_admin(models.Model):
#     id = models.AutoField(primary_key=True,auto_created=True)
#     name = models.CharField(max_field=255, null=True)
#     partner_id = models.OneToOneField(partner, null=True, on_delete=models.CASCADE)

# class program(models.Model):
#     id = models.AutoField(primary_key=True, auto_created=True)
#     name = models.CharField(max_field=255, null=True)
#     partner_id = models.OneToOneField(partner, null=True, on_delete=models.CASCADE)

# class scholar(models.Model):
#     id = models.AutoField(primary_key=True, auto_created=True)
#     partner_id = models.OneToOneField(partner, null=True, on_delete=models.CASCADE)
#     is_verified = models.BooleanField(default=False)
#     photo_verification = 
#     user_id = 
#     status = 

