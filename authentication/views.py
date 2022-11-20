from multiprocessing import context
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
from scholarium.info import *
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed

from . models import ScholarProfile
from .forms import *

import os
import requests, ast, jwt

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
        
        # PRODUCTION CODE
        [email], 
        
        # DEVELOPMENT CODE
        # [TEST_EMAIL_RECEIVER],

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
            # password = request.POST['password']
            email= request.POST['email']
            firstname= request.POST['firstname']
            lastname= request.POST['lastname']

            user_hash, response_message = create_account(username,firstname,lastname,email)
            
            print("username: ", username)
            print("email: ", email)
            print ("hash:", user_hash)
            
            if user_hash != "invalid":
                request.session['user_hash'] = user_hash
                request.session['username'] = username
                request.session['email'] = email
                request.session['first_name'] = firstname
                request.session['last_name'] = lastname
                
                # myuser = User.objects.create_user(username, email, password)
                # myuser.first_name = firstname
                # myuser.last_name = lastname
                # myuser.save()
                
                # ScholarProfile.objects.create(
                # user = myuser,
                # fname = myuser.first_name,
                # lname = myuser.last_name,
                # )
                
                return redirect('success')
            else:
                # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
                print ("ERROR:", response_message)
                return render(request, "authentication/signup.html")

        return render(request, "authentication/signup.html")
    
    except Exception as e:
        print(str(e))
        return render(request, "authentication/signup.html")
    
def signin(request):

    def login_account (username, password):

        payload={'user': username,
        'pass': password }
        files=[]
        headers = {
        'Authorization': API_TOKEN
        }

        response = requests.request("POST", API_LOGIN_ACCOUNT_URL, headers=headers, data=payload, files=files)        
        response_dict = ast.literal_eval(response.text)
        
        print(response.text)
        
        if 'data' in response_dict:
            for data in response_dict['data']:
                user_token = data.get("token")
                expires = data.get("expires")
                response_message = "Successfully Logged In!"
            
        else:
            user_token = ''
            expires = ''
            response_message = response_dict.get("error")
        
        return user_token, expires, response_message
    
    context = {}
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user_token, expires, response_message = login_account(username, password)
        
        if user_token != '':
            
            # COMMAND TO PUT USER_TOKEN INTO SESSIONS
            request.session['user_token'] = user_token
            request.session.modified = True
            
            # PUT JWT TOKEN TO COOKIES
            response = Response()
            response.set_cookie(key='jwt',value=user_token, httponly=True)
            response.data = {
                'jwt': user_token
            }
            
            print('COOKIE RESPONSE:', response.data)
            
            # DISPLAY SESSION ITEMS
            # counter = 0
            # for item in request.session.items():
            #     counter = counter + 1
            #     print("ITEM",counter, ":", item)
                
            # user = authenticate(username=username, password=password)
            # login(request, user)
            # firstname = user.first_name
            
            # user = User.objects.filter(username=username).first()
            # if user is None:
            #     raise AuthenticationFailed('User does not exist.')
            
            # if not user.check_password(password):
            #     raise AuthenticationFailed('Invalid Password.')
            
            context['username'] = username
            context['expires'] = expires
            context['user_token'] = user_token
                  
            return render(request, "authentication/dashboard.html", context)            
        
        else:
            # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
            print ("ERROR:", response_message)
            return render(request, "authentication/signin.html")

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')

def verify_account(request, user_hash):
    
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
        
        return password,response_message
    
    try:
        context = {}
        password, response_message = verify(user_hash)
        
        context['response_message'] = response_message
        context['password'] = password
        
        if password != '':
            print(password)
            print ("SUCCESS:", response_message)
            return render(request, "authentication/verification_successful.html", context)                 
        else:
            print ("ERROR:", response_message)
            return render(request, "authentication/verification_failed.html", context) 
        
    except Exception as e:
        print(str(e))
        return render(request, "authentication/verification_failed.html")

@login_required(login_url='signin')
def profile(request):
    
    return render(request, "profile.html")

@login_required(login_url='signin')
def edit_profile(request):
    
    user = request.user
    fname = request.user.first_name
    lname = request.user.last_name
    form = ScholarProfileForm(instance=user)
    context = {'form':form}
    
    if request.method == 'POST':
        middle_name = request.POST['middle_name']
        profile_pic = request.POST['profile_pic']
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
        region =  request.POST['region']
        province = request.POST['province']
        municipality = request.POST['municipality']

        social =  request.POST['social']
        gender = request.POST['gender']
        birthday =  request.POST['birthday']

        phone = request.POST['phone']
        details_privacy = request.POST['details_privacy']
    
        profile = ScholarProfile(user, fname, lname,
                    middle_name, profile_pic, 
                    emp_status, industry, employer, occupation, 
                    exp_level, degree, university, field, bio, 
                    country, region, province, municipality,
                    social, gender, birthday, phone, details_privacy)
        profile.save()


    return render(request, "edit_profile.html", context)

class DashboardView(APIView):
    def get(self, request):
        # user_token = request.COOKIES.get('jwt')
        user_token = request.session['user_token']
        print("USER TOKEN:", user_token)
        
        if not user_token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        print("PAYLOAD:", payload)
        
        return Response(payload)