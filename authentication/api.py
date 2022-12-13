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
from .models import *
from .api import *
from .forms import *
from .decorators import *
from django.template import Library

from .variables import *
import os, requests, ast, jwt
import json

# GET https://scholarium.tmtg-clone.click/api/me/profile
def user_profile(bearer_token):  
    profile_data = []
    context = {}
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_PROFILE_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        profile_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))
            
    return context

# GET https://scholarium.tmtg-clone.click/api/me/scholarship
def user_programs(bearer_token):
    program_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_PROGRAMS_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                program_list.append(data)
        except Exception as e:
            print(str(e))
            
    return program_list

# GET https://scholarium.tmtg-clone.click/api/me/partners
def user_partners(bearer_token):  
    partner_data = []
    context = {}
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_PARTNERS_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        partner_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))
            
    return context

# GET https://scholarium.tmtg-clone.click/api/me/employment 
def user_employment(bearer_token):  
    employment_data = []
    context = {}  
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_EMPLOYMENT_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        employment_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))
            
    return context

# GET https://scholarium.tmtg-clone.click/api/me/education
def user_education(bearer_token):  
    education_data = []
    context = {}
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_EDUCATION_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        education_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))
    
    return context

# GET https://scholarium.tmtg-clone.click/api/partner/programs/[partner_id]/[program_id]
def get_programs(bearer_token, partner_id,program_id):  
    program_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    if program_id:
        response = requests.request("GET", os.path.join(API_PARTNER_PROGRAMS_URL, str(partner_id)+"/"+str(program_id)), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    program_list.append(data)
            except Exception as e:
                print(str(e))
                              
    else:
        response = requests.request("GET", os.path.join(API_PARTNER_PROGRAMS_URL, str(partner_id)), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    program_list.append(data)
            except Exception as e:
                print(str(e))

    return program_list

# GET https://scholarium.tmtg-clone.click/api/partner/scholarship/[program_id]/[status]
def get_applicants(bearer_token, program_id, status):  
    applicants_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    if status:
        response = requests.request("GET", os.path.join(API_SCHOLAR_UPDATE_URL,str(program_id)+"/"+status), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    applicants_list.append(data)
            except Exception as e:
                print(str(e))
                
    else:
        response = requests.request("GET", os.path.join(API_SCHOLAR_UPDATE_URL,str(program_id)), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    applicants_list.append(data)
            except Exception as e:
                print(str(e))
                
    return applicants_list

# POST https://scholarium.tmtg-clone.click/api/login
def login_account (username, password):
    payload={
        'user': username,
        'pass': password 
    }
    files=[]
    headers = {
    'Authorization': API_TOKEN
    }

    response = requests.request("POST", API_LOGIN_ACCOUNT_URL, headers=headers, data=payload, files=files)        
    response_dict = ast.literal_eval(response.text)
    
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

# POST https://scholarium.tmtg-clone.click/api/user/create
def create_account(request, username, firstname, lastname, email):    
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
        
    for key, value in payload.items():
        request.session['new_'+key] = value
        
    response = requests.request("POST", API_CREATE_ACCOUNT_URL, headers=headers, data=payload, files=files)
    response_dict = ast.literal_eval(response.text)

    if 'data' in response_dict:
        for data in response_dict['data']:
            response_message = data.get("success")
            user_hash = data.get("hash")
    else:
        response_message = response_dict.get("error")
        user_hash = ""         

    return user_hash, response_message

# POST https://scholarium.tmtg-clone.click/api/me/profile 
def update_profile (bearer_token, photo, first_name, last_name, about, country, region, municipality, socials, gender, birthday, contact, date_now, privacy):
    profile_data = []
    context = {}
    payload={
        'photo': photo,
        'first_name': first_name,
        'last_name': last_name,
        'about': about,
        'country': country,
        'municipality': municipality,
        'region': region,
        'socials': socials,
        'gender': gender,
        'birthday': birthday,
        'contact': contact,
        'last_modified': date_now,
        'privacy': privacy
    }
    files=[]
    headers = {
    'Authorization': bearer_token
    }

    response = requests.request("POST", API_USER_PROFILE_URL, headers=headers, data=payload, files=files)        
    response_dict = ast.literal_eval(response.text)
    
    if 'data' in response_dict:
            response_message = "User Account Updated!"
    else:
        response_message = response_dict.get("error")
    
    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-UPDATE VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        profile_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))
            
    return context, response_message

# POST https://scholarium.tmtg-clone.click/api/me/employment 
def update_employment (bearer_token, employ_status, industry, employer, occupation, experience, date_now, privacy):
    employment_data = []
    context = {}
    payload={
        'employ_status': employ_status,
        'industry': industry,
        'employer': employer,
        'occupation': occupation,
        'experience': experience,
        'last_modified': date_now,
        'privacy': privacy
    }
    files=[]
    headers = {
    'Authorization': bearer_token
    }

    response = requests.request("POST", API_USER_EMPLOYMENT_URL, headers=headers, data=payload, files=files)        
    response_dict = ast.literal_eval(response.text)
    
    if 'data' in response_dict:
            response_message = "User Account Updated!"
    else:
        response_message = response_dict.get("error")
    
    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-UPDATE VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        employment_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))

    return context, response_message

# POST https://scholarium.tmtg-clone.click/api/me/education 
def update_education (bearer_token, degree, school,
                        study, date_now, privacy):
    education_data = []
    context = {}
    payload={
        'degree': degree,
        'school': school,
        'study': study,
        'last_modified': date_now,
        'privacy': privacy
    }
    
    files=[]
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("POST", API_USER_EDUCATION_URL, headers=headers, data=payload, files=files)        
    response_dict = ast.literal_eval(response.text)
    
    if 'data' in response_dict:
            response_message = "User Account Updated!"
    else:
        response_message = response_dict.get("error")
    
    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-UPDATE VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        user_data = {key:data.get(key)}
                        education_data.append(user_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e))

    return context, response_message

# PUT https://scholarium.tmtg-clone.click/api/partner/scholarship/[program_id]/[status]
def update_applicant(bearer_token, user_id, program_id, status):  
    payload = json.dumps({
    "data": {
        "user_id": user_id,
        "program_id": program_id,
        "status": status
    }
    })
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("PUT", API_SCHOLAR_UPDATE_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        response_message = "Successfully Updated!"
    else:
        response_message = response_dict.get("error")
    
    return response_message

# PUT https://scholarium.tmtg-clone.click/api/user/verify/[args]
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
