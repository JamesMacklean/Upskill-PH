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
from scholarium.info import *
from . models import ScholarProfile

import os
import requests, ast

def home(request):
    return render(request,"index.html")

def success(request):
    user_hash = request.session.get('user_hash')
    username = request.session.get('username')
    email = request.session.get('email')
    firstname = request.session.get('first_name')
    lastname = request.session.get('last_name')
                
    ############################# FOR MAIL ##############################
    html = render_to_string('emails/email_verification.html', {
        'username': username,
        'first_name': firstname,
        'last_name': lastname,
        'email': email,
        'user_hash': user_hash,
        'link': API_VERIFY_ACCOUNT_URL
    })
    
    send_mail(
        'Title', 
        'Content of the Message', 
        EMAIL_HOST_USER, 
        [TEST_EMAIL_RECEIVER], 
        html_message=html,
        fail_silently=False
    )
    ############################# FOR MAIL ##############################
    
    return render(request,"welcome.html")

def signup(request):

    def create_account(username,firstname,lastname,email):     
        payload={
            'username': username,
            'first_name': firstname,
            'last_name': lastname,
            'email': email
            }
        
        files=[]
        
        headers = {
        'Authorization': API_TOKEN
        }

        response = requests.request("POST", API_CREATE_ACCOUNT_URL, headers=headers, data=payload, files=files)

        response_dict = ast.literal_eval(response.text)
        
        if 'data' in response_dict:
            for data in response_dict['data']:
                response_message = data.get("success")
                user_hash = data.get("hash")
        else:
            response_message = response_dict.get("error")
            user_hash = "invalid"         

        return user_hash, response_message
        
    try:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            email= request.POST['email']
            firstname= request.POST['firstname']
            lastname= request.POST['lastname']

            user_hash, response_message = create_account(username,firstname,lastname,email)
            
            print("username: ", username)
            print("email: ", email)
            print ("hash:", user_hash)
            
            if user_hash is not "invalid":
                request.session['user_hash'] = user_hash
                request.session['username'] = username
                request.session['email'] = email
                request.session['first_name'] = firstname
                request.session['last_name'] = lastname
                return redirect('success')
            else:
                # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
                print ("ERROR:", response_message)
                return render(request, "authentication/signup.html")
            
            ############################## FOR DJANGO ##############################
            # if User.objects.filter(username=username):
            #     messages.error(request, "username already exists")
            
            # if User.objects.filter(email=email):
            #     messages.error(request, "email already exists")

            # myuser = User.objects.create_user(username, email, password)
            # myuser.first_name = firstname
            # myuser.last_name = lastname
            
            # myuser.save()
            # return redirect('success')
            ############################## FOR DJANGO ##############################
            
        return render(request, "authentication/signup.html")
    
    except Exception as e:
        print(str(e))
        return render(request, "authentication/signup.html")

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

def verify_account(request, username, user_hash):
    
    def verify(user_hash):
        
        payload={}
        files={}
        headers = {
        'Authorization': API_TOKEN
        }

        response = requests.request("PUT", os.path.join(API_VERIFY_ACCOUNT_URL, user_hash), headers=headers, data=payload, files=files)
        

        response_dict = ast.literal_eval(response.text)
        
        if 'data' in response_dict:
            for data in response_dict['data']:
                response_message = data.get("success")
                password = data.get("password")
        else:
            response_message = response_dict.get("error")
            password=''   
        
        return response_message,password
    
    try:
        context = {}
        
        response_message, password = verify(user_hash)
        
        context['response_message'] = response_message
        context['password'] = password
        
        if password is not '':
            print(password)
            print ("SUCCESS:", response_message)
            return render(request, "authentication/verification_successful.html", context)                 
        else:
            print ("ERROR:", response_message)
            return render(request, "authentication/verification_failed.html") 
        
    except Exception as e:
        print(str(e))
        return render(request, "authentication/verification_failed.html")

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