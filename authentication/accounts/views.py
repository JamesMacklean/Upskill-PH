from multiprocessing import context
from re import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from scholarium import settings
from datetime import datetime, timedelta
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from scholarium.info import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView
from ..api import *
from django.template import Library
from django.core.paginator import Paginator

import os, requests, ast, jwt, csv

def success(request, user_hash):
    """"""
    template_name = "success.html"
    context = {}

    username = request.session.get('new_username')        
    first_name = request.session.get('new_first_name')
    last_name = request.session.get('new_last_name')
    email = request.session.get('new_email')
    
    return render(request,template_name, context)

def verify_account(request, user_hash):
    """"""
    template_successful = "authentication/verification_successful.html"
    template_failed = "authentication/verification_failed.html"
    context = {}
    
    try:
        email, response_message = verify(user_hash)
                
        if email:
            print ("SUCCESS:", response_message, flush=True)
            try:
                original_url = request.session['original_url']
            except Exception as e:
                print(str(e), flush=True)
                original_url = ""
            
            print (f'ORIGINAL URL: {original_url}', flush=True)
            context['original_url'] = original_url
            context['domain'] = settings.DOMAIN
            
            print(template_successful, flush=True)
            
            return render(request, template_successful, context)                
        else:
            print ("ERROR:", response_message, flush=True)
            return render(request, template_failed, context) 
        
    except Exception as e:
        print(str(e), flush=True)
        return render(request, template_failed, context)
    
def signup(request):
    """"""
    template_name = "authentication/signup.html"
    context = {}
        
    try:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']

            user_hash, redirect_url, response_message = create_account(request, email, password)
            context['response_message'] = response_message

            try:
                original_url = request.session['original_url']
            except Exception as e:
                print(str(e), flush=True)
                original_url = ""

            if user_hash:
                #### MODAL RESPONSE KUNG NAGWORK BA ANG SIGN UP
                response_message = "success"
                # domain = f'http://{request.get_host()}'
                # request.session['user_hash'] = user_hash
                # request.session.modified = True

                print(f'NEW ACCOUNT DETAILS: {email, password, user_hash, redirect_url, original_url}', flush=True)
                
                ############################# FOR MAIL ##############################
                html = render_to_string('emails/email_verification.html', {
                    'email': email,
                    'user_hash': user_hash,
                    'redirect_url': redirect_url,
                    'original_url': original_url,
                    'link': API_VERIFY_ACCOUNT_URL,
                    ########## ORIGINAL CODE ##########
                    'domain': f'{settings.DOMAIN}',
                    'accounts_domain': f'{settings.ACCOUNTS_DOMAIN}',
                    ########## FOR TEST CODE ##########
                    # 'domain': domain,
                    
                })
                try:
                    send_mail(
                        'Welcome to Upskill PH', 
                        'Content of the Message', 
                        settings.EMAIL_HOST_USER, 
                        ########## ORIGINAL CODE ##########
                        # [email], 
                        ########## FOR TEST CODE ##########
                        [TEST_EMAIL_RECEIVER],
                        html_message=html,
                        fail_silently=False
                    )
                    print(f'Verification email sent to {email}', flush=True)
                except Exception as e:
                    print("Failed to send email:", str(e), flush=True)
                ############################# FOR MAIL ##############################
            
            print(f'SIGN UP: {response_message}', flush=True)
            
    except Exception as e:
        print(str(e), flush=True)
        context['response_message'] = "error"
    
    return render(request, template_name, context)

def signin(request): 
    """"""
    template_name = "authentication/signin.html"
    context = {}
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        domain = f'http://{request.get_host()}'
        
        user_token, expires, redirect_url, response_message = login_account(email, password)
        
        #### MODAL RESPONSE KUNG NAGWORK BA ANG SIGN IN
        print(f'SIGN IN: {response_message}', flush=True)
        
        if user_token:            
            scholarships = user_programs(user_token) 
            partners = user_partners(user_token)
                             
            try:    
                request.session['user_token'] = user_token
                request.session['expires'] = expires
                request.session['redirect_url'] = redirect_url
                request.session['is_scholar'] = scholarships
                request.session['is_partner'] = partners
                request.session.modified = True
                
                payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])
                # SAVE JWT PAYLOAD INTO SESSIONS
                for key,value in payload.items():
                    if key == 'data':
                        for key,value in payload['data'].items():
                            request.session[key] = value
                            request.session.modified = True
                # PRINT SESSION ITEMS
                for key, value in request.session.items():
                    print('{}: {}'.format(key, value), flush=True)
                                        
            except jwt.ExpiredSignatureError:
                raise Http404
            
            # context['username'] = username
            context['expires'] = expires
            context['user_token'] = user_token
            
            # CHECK IF THE REQUEST IS REDIRECTION
            try:
                next_page = request.session.get('original_url')
                print('')
                print(f"SIGN IN original_url:{next_page}", flush=True)
            except:
                next_page = ""
                  
            response = None
            
            # IF REDIRECTION SIYA, PUNTA SA NEXT PAGE, PERO KUNG HINDI, SA DASHBOARD
            if next_page:
                try:
                    clear_session(request,'original_url')
                    response = redirect(f'{domain}{next_page}')
                except Exception as e:
                    print(str(e), flush=True)
            
            else:
                response = redirect(f'{domain}')
            
            # Set cookies
            print("SETTING COOKIES...", flush=True) 
            # response.set_cookie('cookie_name', 'cookie_value')
            response.set_cookie('_ups_aut', user_token, expires=expires, samesite='None', secure=True)

            # for key, value in payload['data'].items():
            #     response.set_cookie(key, value)
            #     print(f"Set cookie: {key} = {value}")
            
            return response

        else:
            # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
            print ("SIGN IN ERROR:", response_message, flush=True)
            context['response_message'] = response_message
            return render(request, template_name, context)

    return render(request, template_name, context)

def clear_session(request,key):
    try:
        del request.session[key]  
        request.session.modified = True  
    except KeyError:
        pass
    
    return HttpResponse(key, "session data cleared")