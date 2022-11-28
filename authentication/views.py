from multiprocessing import context
from re import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from scholarium import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from scholarium.info import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .forms import *
from .decorators import *

import os, requests, ast, jwt
class SessionChecker(APIView):
    def get(self, request):
        
        # CHECK IF USER IS AUTHENTICATED
        try:            
            
            # user_token = request.COOKIES.get('jwt')    
            try:    
                user_token = request.session['user_token']
                payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])
                
                # SAVE JWT PAYLOAD INTO SESSIONS
                for key,value in payload.items():
                    if key == 'data':
                        for key,value in payload['data'].items():
                            request.session[key] = value
            
                # DISPLAY SESSION ITEMS
                for key, value in request.session.items():
                    print('{}: {}'.format(key, value))
                      
                return Response(payload)
                      
            except jwt.ExpiredSignatureError:
                # raise AuthenticationFailed('Unauthenticated!')
                raise Http404
            
        except KeyError:
            raise Http404

def authenticate_user(request):
    
    try:
        
        # user_token = request.COOKIES.get('jwt')    
        try:   
            user_token = request.session['user_token'] 
            print ("AUTHENTICATE:",user_token)
            payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])
        
            # SAVE JWT PAYLOAD INTO SESSIONS
            for key,value in payload.items():
                if key == 'data':
                    for key,value in payload['data'].items():
                        request.session[key] = value   
            return True
        
        except jwt.ExpiredSignatureError:
            return False
        
    except KeyError:
        return False
    
def clear_session(request,key):
    
    try:
        del request.session[key]
    except KeyError:
        pass
    return HttpResponse(key, "session data cleared")

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
        
        ########## ORIGINAL CODE ##########
        [email], 
        ########## FOR TEST CODE ##########
        # [TEST_EMAIL_RECEIVER],

        html_message=html,
        fail_silently=False
    )
    ############################# FOR MAIL ##############################
    
    return render(request,"welcome.html")

def signup(request):

    def create_account(username,firstname,lastname,email):    
        
        ###################### https://scholarium.tmtg-clone.click/api/user/create ###################### 
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
        ###################### https://scholarium.tmtg-clone.click/api/user/create ###################### 
        
        print(response.text)
        
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
                
                # ICOCONFIGURE PA ITO NA DAPAT SA PROFILE TABLES NG API MAIISTORE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!          
                # Profile.objects.create(
                # user = username,
                # fname = firstname,
                # lname = lastname,
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

    context = {}
    
    def login_account (username, password):

        ###################### https://scholarium.tmtg-clone.click/api/login ######################
        payload={'user': username,
        'pass': password }
        files=[]
        headers = {
        'Authorization': API_TOKEN
        }

        response = requests.request("POST", API_LOGIN_ACCOUNT_URL, headers=headers, data=payload, files=files)        
        response_dict = ast.literal_eval(response.text)
        
        print(response.text)
        ###################### https://scholarium.tmtg-clone.click/api/login ######################
        
        
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
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user_token, expires, response_message = login_account(username, password)
        
        if user_token != '':
            
            # PUT JWT TOKEN TO COOKIES
            # response = Response()
            # response.set_cookie(key='jwt',value=user_token, httponly=True)
            # response.data = {
            #     'jwt': user_token
            # }
            
            # print('COOKIE RESPONSE:', response.data)
            
            ############################# FOR AUTHENTICATION ##############################
            try:    
                request.session['user_token'] = user_token
                payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])
            
                # SAVE JWT PAYLOAD INTO SESSIONS
                for key,value in payload.items():
                    if key == 'data':
                        for key,value in payload['data'].items():
                            request.session[key] = value
            
                # PRINT SESSION ITEMS
                for key, value in request.session.items():
                    print('{}: {}'.format(key, value))
                                
            except jwt.ExpiredSignatureError:
                # raise AuthenticationFailed('Unauthenticated!')
                raise Http404
            ############################# FOR AUTHENTICATION ##############################
          
            context['username'] = username
            context['expires'] = expires
            context['user_token'] = user_token
            
            # CHECK IF THE REQUEST IS REDIRECTION
            try:
                next_page = request.session['url']
            except:
                next_page = ""
            
            # IF REDIRECTION SIYA, PUNTA SA NEXT PAGE, PERO KUNG HINDI, SA DASHBOARD
            if next_page == "":
                return render(request, "authentication/dashboard.html", context)
            else:
                return HttpResponseRedirect(next_page)

        else:
            # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
            print ("ERROR:", response_message)
            return render(request, "authentication/signin.html")

    return render(request, "authentication/signin.html")

def signout(request):
    
    # CLEAR SESSIONS
    try:   
        for key in list(request.session.keys()):
            del request.session[key]
    except KeyError as e:
        print (e)
        
    return redirect('home')

def verify_account(request, user_hash):
    
    def verify(user_hash):
        
        ###################### https://scholarium.tmtg-clone.click/api/user/verify/[args] ###################### 
        payload={}
        files={}
        headers = {
        'Authorization': API_TOKEN
        }

        response = requests.request("PUT", os.path.join(API_VERIFY_ACCOUNT_URL, user_hash), headers=headers, data=payload, files=files)
        
        response_dict = ast.literal_eval(response.text)
        ###################### https://scholarium.tmtg-clone.click/api/user/verify/[args] ###################### 
        
        print(response.text)
        
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
        context['domain'] = DOMAIN
        
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

def profile(request):
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "profile"
        return HttpResponseRedirect('signin?next=profile')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    context = {}

    # user = request.user

    # program = Program.objects.filter(is_active=True)
    # available = []
    # ongoing = []

    # for group in program.groups.all().filter(is_active=True):
    #     programs = {}
    #     if group.type == "AB":
    #         available.append(programs)
    #     else:
    #         ongoing.append(programs)

    # form = ProfileForm(instance=user)
    # context = {
    #     'form':form,
    #     'program':program,
    # }
    
    return render(request, "profile.html",context)

def partner(request):
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "partner"
        return HttpResponseRedirect('signin?next=partner')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    return render(request, "partner_dashboard.html")

def edit_profile(request):
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "edit"
        return HttpResponseRedirect('signin?next=edit')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    context = {}
    # user = request.user
    # form = ProfileForm(instance=user)
    # context = {'form':form}
    
    return render(request, "edit_profile.html", context)

def program(request, slug):
    """"""
    template_name = "scholar_programs.html"
    context = {}

    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "program/"+slug
        return HttpResponseRedirect('signin?next=program/'+slug)
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    program = get_object_or_404(Program, slug=slug)
    
    context['program']= program
    context['partner_logos']= Program.objects.partner_logo
    return render(request, template_name, context)
