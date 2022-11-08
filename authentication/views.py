from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from scholarium import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

from . models import ScholarProfile

import authentication

# For API
# pip install requests
import requests

# Create your views here.

def home(request):
    return render(request,"index.html")

def success(request):
    return render(request,"welcome.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email= request.POST['email']
        firstname= request.POST['firstname']
        lastname= request.POST['lastname']
        
        ############################## FOR API ##############################
        url = "https://scholarium.tmtg-clone.click/api/basic/create"

        payload={'username': username,
        'first_name': firstname,
        'last_name': lastname,
        'email': email}
        files=[

        ]
        headers = {
        'Authorization': 'Basic e3tDT19JRH19Ont7QVBJX0tFWX19'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        print(response.text)
        messages.error(response)
        
        ############################## FOR API ##############################
        
        # if User.objects.filter(username=username):
        #         messages.error(request, "username already exists")
        
        # if User.objects.filter(email=email):
        #     messages.error(request, "email already exists")

        # myuser = User.objects.create_user(username, email, password)
        # myuser.first_name = firstname
        # myuser.last_name = lastname
        
        # myuser.save()
        
        return redirect('success')

    # return render(request, "authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, "authentication/dashboard.html", {'first_name': firstname})

        else: 
            messages.error(request, "Invalid username/password")
            return redirect('home')

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser= None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('signin')
    else:
        return(request, "activation_failed.html")

def profile(request):

    if request.user.is_authenticated:
        firstname = request.user.first_name
        lastname = request.user.last_name

    return render(request, "profile.html", {'firstname':firstname, 'lastname':lastname})

def edit_profile(request):
    
    first_name = request.POST['first_name']
    middle_name = request.POST['middle_name']
    last_name = request.POST['last_name']
    profile_picture = request.POST['profile_picture ']
    emp_status = request.POST['emp_status']
    industry = request.POST['industry']
    employer = request.POST['employer']
    occupation = request.POST['occupation']
    exp_level = request.POST['exp_level']
    degree = request.POST['degree']
    university = request.POST['university']
    field = request.POST['field']
    bio = request.POST['bio']
    country = request.POST['country']
    region = request.POST['region']
    province = request.POST['province']
    municipality = request.POST['municipality']
    socials = request.POST['socials']
    gender = request.POST['gender']
    gender = request.POST['gender']
    birthday = request.POST['birthday']
    phone = request.POST['phone']
    details_privacy = request.POST['details_privacy']

    scholar = ScholarProfile.objects.create(first_name, middle_name, last_name, profile_picture, emp_status, industry, employer, occupation, exp_level, degree, university, field, bio, country, region, municipality, socials, gender, birthday, phone, details_privacy)
    scholar.save()
    return render(request, "edit_profile.html")
