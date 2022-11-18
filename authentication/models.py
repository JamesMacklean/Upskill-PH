from email.mime import application
from tabnanny import verbose
from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class User():
#     id = models.AutoField(primary_key=True)
#     username = 
#     password 
#     email 
#     date_joined
#     last_login
#     hash 
#     is_global
#     is_admin
#     is_staff
#     status 

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
            User, null=True,
            on_delete=models.CASCADE)

    fname = models.CharField(max_length=200, null=True)
    middle_name = models.CharField(max_length=200, null=True)
    lname = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(null=True, blank=True)    
    about = models.CharField(max_length=500, null=True)
    country = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=200, null=True)
    province = models.CharField(max_length=200, null=True)
    municipality = models.CharField(max_length=200, null=True)
    gender = models.CharField(max_length=200, null=True)
    birthday = models.DateTimeField(null=True)
    social = models.CharField(max_length=200, null=True)
    phone = models.IntegerField(null=True)
    details_privacy = models.CharField(max_length=200, null=True)
    last_modified= models.DateField(null=True)
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="profiles"
    )
    class Meta:
        # ordering = ['order']
        verbose_name_plural = "Profiles"

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

class Education(models.Model):
    id = models.AutoField(primary_key=True)
    degree = models.CharField(max_length=2,null=True)
    school = models.CharField(max_length=200,null=True)
    study = models.CharField(max_length=200, null=True)
    last_modified = models.DateTimeField(null=True)
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="education_profiles"
    )

class Employment(models.Model):
    id = models.AutoField(primary_key=True)
    employ_status = models.CharField(max_length=255, null=True)
    industry = models.CharField(max_length=255, null=True)
    employer = models.CharField(max_length=255, null=True)
    occupation = models.CharField(max_length=255, null=True)
    experience = models.CharField(max_length=255, null=True)
    last_modified = models.DateTimeField(null=True)
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="employment_profiles"
    )

class Partner(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_field=255, null=True)

class PartnerAdmin(models.Model):
    id = models.AutoField(primary_key=True,auto_created=True)
    name = models.CharField(max_field=255, null=True)
    partner_id = models.ForeignKey(
        Partner, 
        null=True, 
        on_delete=models.CASCADE,
        related_name="partner_admin"
        )

class Program(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_field=255, null=True)
    url= models.URLField(null=True)
    image_url= models.URLField(null=True)
    partner_id = models.ForeignKey(
        Partner, 
        null=True, 
        on_delete=models.CASCADE,
        related_name="programs"
        )
class Scholar(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    partner_id = models.ForeignKey(
        Partner, 
        null=True, 
        on_delete=models.CASCADE,
        related_name="partners"
        )
    is_verified = models.BooleanField(default=False)
    photo_verification = models.URLField()
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="employment_profiles"
    )
    status = models.BooleanField(null=True) 

class Application(models.Model):
    """
    """
    SHORTLIST = "SL"
    WAITLIST = "WL"
    APPROVED = "AP"
    REJECTED = "RE"
    STATUS_CHOICES = (
        (SHORTLIST, "Shortlisted"),
        (WAITLIST, "Waitlisted"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected")
    )
    id = models.AutoField(primary_key=True, auto_created=True)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Scholarium username"
    )
    program = models.ForeignKey(
        Program,
        null=True,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Program"
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=SHORTLIST)
    class Meta:
        verbose_name_plural = "Scholarship Applications"

    def __str__(self):
        return "{}: {}".format(self.profile.user.username, self.program.name)

    def shortlist(self):
        if self.status != self.SHORTLIST:
            self.status = self.SHORTLIST
            self.save()

    def waitlist(self):
        if self.status != self.WAITLIST:
            self.status = self.WAITLIST
            self.save()

    def approve(self):
        if self.status != self.APPROVED:
            self.status = self.APPROVED
            self.save()

    def reject(self):
        if self.status != self.REJECTED:
            self.status = self.REJECTED
            self.save()
