from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ScholarProfile(models.Model):
    # EMP_CHOICES = (
    #     ("FT", "Full time"),
    #     ("PT", "Part time"),
    #     ("SE", "Self Employed"),
    #     ("HM", "Homemaker"),
    #     ("UE", "Unemployed"),
    #     ("RT", "Retired"),
    #     ("UW", "Unable to work"),
    # )
    # INDUSTRY_CHOICES = (
    #     ("AG","Agriculture and Land"),
    #     ("CS","Chemical Sciences"),
    #     ("CE","Construction"),
    #     ("CR","Creatives"),
    #     ("DT","Digital Technologies"),
    #     ("EN","Energy"),
    #     ("EM","Engineering and Manufactuting"),
    #     ("FS","Financial services"),
    #     ("FD","Food and drink"),
    #     ("HC","Healthcare"),
    #     ("LS","Life Sciences"),
    #     ("SC","Social Care"),
    #     ("TO","Tourism"),
    #     ("TR","Transport"),
    # )
    # EXPLEVEL_CHOICES = (
    #     ("IN","Intern/Trainee"),
    #     ("JR","Junior / Entry Level (0 - 2 years experience)"),
    #     ("ML","Mid-level (2+ years experience)"),
    #     ("LM","Lead / Manager"),
    #     ("SM","Senior Manager"),
    #     ("EL","Executive Level"),
    #     ("NA","Not Applicable"),
    # )
    # DEGREE_CHOICES = (
    #     ("LD","Less than high school diploma or equivalent"),
    #     ("JH","Junior high diploma"),
    #     ("SH","Senior high diploma"),
    #     ("CU","Some units in college but no degree"),
    #     ("AS","Associate degree"),
    #     ("BS","Bachelor's degree"),
    #     ("MD","Master's degree"),
    #     ("DD","Doctorate degree"),
    # )
    # FIELD_CHOICES = (
    #     ("BU","Business"),
    #     ("CS","Computer Science"),
    #     ("EN","Engineering"),
    #     ("MS","Mathematics and Statistics"),
    #     ("PS","Physical Sciences"),
    #     ("BS","Biological Sciences"),
    #     ("SS","Social Sciences"),
    #     ("HP","Health Professions"),
    #     ("LP","Legal Professions"),
    #     ("ED","Education"),
    #     ("AH","Arts and Humanities"),
    #     ("OT","Other"),
    #     ("NA","Not Applicable"),
    # )

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
        return self.user
