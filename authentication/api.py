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


# GET https://scholarium.tmtg-clone.click/v1/me
def user_details(bearer_token):  
    user_data = []
    context = {}
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        collected_data = {key:data.get(key)}
                        user_data.append(collected_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e), flush=True)
            
    return context

# GET https://scholarium.tmtg-clone.click/v1/me/profile
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
            print(str(e), flush=True)
            
    return context

# GET https://scholarium.tmtg-clone.click/v1/me/scholarship
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
            print(str(e), flush=True)
            
    return program_list

# GET https://scholarium.tmtg-clone.click/v1/me/partners
def user_partners(bearer_token):  
    partner_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_USER_PARTNERS_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                partner_list.append(data)
        except Exception as e:
            print(str(e), flush=True)
            
    return partner_list

# GET https://scholarium.tmtg-clone.click/v1/me/employment 
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
            print(str(e), flush=True)
            
    return context

# GET https://scholarium.tmtg-clone.click/v1/me/education
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
            print(str(e), flush=True)
    
    return context

# GET https://scholarium.tmtg-clone.click/v1/admin/users/[user_id]/[endpoint]
def get_user_details(bearer_token, user_id, endpoint):
    payload={}
    context = {}
    headers = {
    'Authorization': bearer_token
    }

    url = ADMIN_URL + f"users/{user_id}/{endpoint}"
    
    response = requests.request("GET", url, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e), flush=True)
    
    return context


# GET https://scholarium.tmtg-clone.click/v1/admin/users
def users_list(bearer_token, user_id=None, endpoint=None):  
    if user_id and endpoint:
        return get_user_details(bearer_token, user_id, endpoint)
    
    users = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", ADMIN_URL + "users/", headers=headers, data=payload)
    response_dict = json.loads(response.text)

    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                users.append(data)
        except Exception as e:
            print(str(e), flush=True)
            
    return users

# GET https://scholarium.tmtg-clone.click/v1/partner/[partner_id]/programs/[program_id]
def get_programs(bearer_token, partner_id,program_id):  
    program_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    if program_id:
        response = requests.request("GET", os.path.join(API_PARTNER_URL, str(partner_id)+"/programs/"+str(program_id)), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    program_list.append(data)
            except Exception as e:
                print(str(e), flush=True)
                              
    else:
        response = requests.request("GET", os.path.join(API_PARTNER_URL, str(partner_id)+"/programs"), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    program_list.append(data)
            except Exception as e:
                print(str(e), flush=True)

    return program_list

# GET https://scholarium.tmtg-clone.click/v1/partner/program/[slug]
def get_program_through_slug(bearer_token, slug):  
    program_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", os.path.join(API_PROGRAM_SLUGS_URL, str(slug)), headers=headers, data=payload)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                program_list.append(data)
        except Exception as e:
            print(str(e), flush=True)

    return program_list

# GET https://api.coursera.org/api/businesses.v1/PigzUIPvRnWQ-YVaCKAmCw/programs
# def get_dict_programs(bearer_token):
#     program_list = []
#     payload = {}
#     headers = {
#     'Authorization': 'Bearer '+ bearer_token
#     }

#     response = requests.request("GET", DICT_PROGRAMS_URL, headers=headers, data=payload)
#     response_dict = json.loads(response.text)
    
#     # 'id', 'name', 'tagline', 'url', 'contentIds': [{'contentId', 'contentType'}]}
#     if 'elements' in response_dict:
#         try:
#             for data in response_dict['elements']:
#                 program_list.append(data)
#         except Exception as e:
#             print(str(e), flush=True)

#     return program_list

# GET https://scholarium.tmtg-clone.click/v1/partner/[partner_id]/scholarship/[program_id]/status/[status]
def get_applicants(bearer_token, partner_id, program_id, status):  
    applicants_list = []
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    if status:
        response = requests.request("GET", os.path.join(API_PARTNER_URL,str(partner_id)+"/scholarship/"+str(program_id)+"/status/"+status), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    applicants_list.append(data)
            except Exception as e:
                print(str(e), flush=True)
                
    else:
        response = requests.request("GET", os.path.join(API_PARTNER_URL,str(partner_id)+"/scholarship/"+str(program_id)), headers=headers, data=payload)
        response_dict = json.loads(response.text)
        
        if 'data' in response_dict:
            try:
                for data in response_dict['data']:
                    applicants_list.append(data)
            except Exception as e:
                print(str(e), flush=True)
                
    return applicants_list

# GET https://scholarium.tmtg-clone.click/v1/admin/codes/[code]
def license_code(bearer_token,code):  
    license_codes = []
    context = {}
    payload={}
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("GET", API_LICENSE_CODE_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-GET VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                license_codes.append(data)
                        
        except Exception as e:
            print(str(e), flush=True)
            
    # return context
    return license_codes

# POST https://scholarium.tmtg-clone.click/v1/login
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
    
    # response_dict = ast.literal_eval(response.text)
    
    try:
        response_dict = response.json()
    except json.JSONDecodeError:
        return '', '', '', 'Invalid response format'
    
    if 'data' in response_dict:
        for data in response_dict['data']:
            user_token = data.get("token")
            expires = data.get("expires")
            redirect_url = data.get("redirect")
            response_message = "Successfully Logged In!"
    else:
        user_token = ''
        expires = ''
        redirect_url = ''
        response_message = response_dict.get("error")
    
    return user_token, expires, redirect_url, response_message

# POST https://scholarium.tmtg-clone.click/v1/user/add
def create_account(request, email, password):    
    payload={
        'email': email,
        'password': password
        }
    files=[]
    headers = {
    'Authorization': API_TOKEN
    }
        
    for key, value in payload.items():
        request.session['new_'+key] = value
        
    response = requests.request("POST", API_CREATE_ACCOUNT_URL, headers=headers, data=payload, files=files)
    # response_dict = ast.literal_eval(response.text)
    
    try:
        response_dict = response.json()
    except json.JSONDecodeError:
        return '', '', '', 'Invalid response format'
    
    if 'data' in response_dict:
        for data in response_dict['data']:
            response_message = data.get("success")
            user_hash = data.get("hash")
            redirect_url = data.get("redirect")
    else:
        response_message = response_dict.get("error")
        user_hash = ""
        redirect_url = ""
    
    return user_hash, redirect_url, response_message

# POST https://scholarium.tmtg-clone.click/v1/me/profile 
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
            print(str(e), flush=True)
            
    return context, response_message

# POST https://scholarium.tmtg-clone.click/v1/me/employment 
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
            print(str(e), flush=True)

    return context, response_message

# POST https://scholarium.tmtg-clone.click/v1/me/education 
def update_education (bearer_token, degree, school, study, date_now, privacy):
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
            print(str(e), flush=True)

    return context, response_message

# POST https://scholarium.tmtg-clone.click/v1/partner/programs 
def update_program (bearer_token, program_id, name, description, partner_id, logo, image, start_date, end_date, registration_end, badge, certificate, date_now):
    updated_data = []
    context = {}
    payload={
        'program_id': program_id,
        'name': name,
        'description': description,
        'partner_id': partner_id,
        'logo': logo,
        'image': image,
        'start_date': start_date,
        'end_date': end_date,
        'registration_end': registration_end,
        'badge': badge,
        'certificate': certificate,
        'last_modified': date_now
    }
    
    files=[]
    headers = {
    'Authorization': bearer_token
    }
    
    response = requests.request("POST", API_PARTNER_PROGRAMS_URL, headers=headers, data=payload, files=files)        
    response_dict = ast.literal_eval(response.text)
    
    if 'data' in response_dict:
            response_message = "Program Updated!"
    else:
        response_message = response_dict.get("error")
    
    # AUTO-ADD SA CONTEXT NG MGA KEYS NA NA-UPDATE VIA API
    if 'data' in response_dict:
        try:
            for data in response_dict['data']:
                for key, value in data.items():
                    if value is not None:
                        program_data = {key:data.get(key)}
                        updated_data.append(program_data)
                        context[key] = data.get(key)
                        
        except Exception as e:
            print(str(e), flush=True)

    return context, response_message

# POST https://scholarium.tmtg-clone.click/v1/me/scholarship
def scholar_apply(bearer_token, program_id):
    payload={'program_id': program_id}
    headers = {
    'Authorization': bearer_token,
    }

    response = requests.request("POST", API_SCHOLAR_APPLY_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        response_message = "Successfully Applied!"
    else:
        response_message = response_dict.get("error")

    return response_message

# POST https://scholarium.tmtg-clone.click/v1/me/password
def change_password(bearer_token, old_password, new_password):
    payload={
        'oldpw': old_password,
        'newpw': new_password
    }
    files=[
    ]
    
    headers = {
    'Authorization': bearer_token
    }

    response = requests.request("POST", API_UPDATE_PASSWORD_URL, headers=headers, data=payload, files=files)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        response_message = "Successfully Updated Password!"
    else:
        response_message = response_dict.get("error")

    return response_message

# PUT https://scholarium.tmtg-clone.click/v1/partner/scholarship/[program_id]/[status]
def update_applicant(bearer_token, user_id, partner_id, program_id, status):  
    payload = json.dumps({
    "data": {
        "user_id": user_id,
        "partner_id": partner_id,
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

# PUT https://scholarium.tmtg-clone.click/v1/user/verify/[args]
def verify(user_hash):

    payload={}
    files={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("PUT", os.path.join(API_VERIFY_ACCOUNT_URL, user_hash), headers=headers, data=payload, files=files)
    
    try:
        response_dict = response.json()
    except json.JSONDecodeError:
        return '', '', '', 'Invalid response format'
    
    if 'data' in response_dict:
        for data in response_dict['data']:
            response_message = data.get("success")
            email = data.get("email")
    else:
        response_message = response_dict.get("error")
        email = ''
        password = ''
    
    return email, response_message

# GET https://discovery.coursebank.ph/api/v1/courses/?limit=6&
def get_courses():  
    courses = []
    response = requests.get(COURSEBANK_COURSES_URL)
    
    if response.status_code == 200:
        
        try:
            courses_data = response.json()
        except json.JSONDecodeError:
            return '', '', '', 'Invalid response format'
        
        if 'results' in courses_data:
            try:
                for data in courses_data['results']:
                    courses.append(data)
            except Exception as e:
                print(str(e), flush=True)
    
    return courses

# GET https://coursebank.ph/api/users/
def get_coursebank_users():  
    users = []
    response = requests.get(COURSEBANK_USERS_URL)
    
    if response.status_code == 200:
        try:
            user_data = response.json()
        except json.JSONDecodeError:
            return '', '', '', 'Invalid response format'
        
        if 'results' in user_data:
            try:
                for data in user_data['results']:
                    users.append(data)
            except Exception as e:
                print(str(e), flush=True)
    
    return users

# PUT https://scholarium.tmtg-clone.click/v1/me/enroll/code
def enroll_code(bearer_token, program_id, code):  

    program_id = int(program_id)
    payload = f'{{\r\n    "data": \r\n        {{\r\n            "program_id\":{program_id},\r\n             "code":"{code}"\r\n        }}\r\n}}'
    headers = {
        'Content-Type': 'text/plain',
        'Authorization': bearer_token
    }
    
    response = requests.request("PUT", API_ENROLL_CODE_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        response_message = "License Code Verified!"
    else:
        response_message = response_dict.get("error")
    
    return response_message

# PUT https://scholarium.tmtg-clone.click/v1/me/enroll/program
def enroll_program(bearer_token, program_id):  

    program_id = int(program_id)
    payload = json.dumps({
        "data": {
            "program_id": program_id
        }
    })
    headers = {
        'Content-Type': 'text/plain',
        'Authorization': bearer_token
    }
    
    response = requests.request("PUT", API_ENROLL_PROGRAM_URL, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    
    if 'data' in response_dict:
        response_message = "License Code Verified!"
    else:
        response_message = response_dict.get("error")
    return response_message

# GET INITIAL CODE
# def get_initial_code():
#     try:
#         code = CourseraToken.objects.get(item='initial_code')
#         return code.value
#     except CourseraToken.DoesNotExist:
#         return None
    
# def get_refresh_token_from_django():
#     try:
#         token = CourseraToken.objects.get(item='refresh_token')
#         return token.value
#     except CourseraToken.DoesNotExist:
#         return None
    
# POST https://accounts.coursera.org/oauth2/v1/token
# def get_refresh_token():  

#     payload = 'redirect_uri=http%3A%2F%2Flocalhost%3A9876%2Fcallback&client_id=' + COURSERA_CLIENT_ID + "&client_secret=" + COURSERA_CLIENT_SECRET + "&access_type=offline&code=" + get_initial_code() + "&Content-Type=application%2Fx-www-form-urlencoded&grant_type=authorization_code"
    
#     headers = {
#     'Content-Type': 'application/x-www-form-urlencoded',
#     }

#     response = requests.request("POST", COURSERA_TOKEN_URL, headers=headers, data=payload)
#     response_dict = json.loads(response.text)
    
#     if 'refresh_token' in response_dict:
#         new_refresh_token =  response_dict.get("refresh_token")
#         new_access_token =  response_dict.get("access_token")
        
#         try:
#             refresh_token_entry = CourseraToken.objects.get(item='refresh_token')
#             access_token_entry = CourseraToken.objects.get(item='access_token')
#         except CourseraToken.DoesNotExist:
#             refresh_token_entry = CourseraToken(item='refresh_token', value=new_refresh_token)
#             refresh_token_entry.save()
#             access_token_entry = CourseraToken(item='access_token', value=new_access_token)
#             access_token_entry.save()
#         else:
#             refresh_token_entry.value = new_refresh_token
#             refresh_token_entry.save()
#             access_token_entry.value = new_access_token
#             access_token_entry.save()

#     return (response.text)

# POST https://accounts.coursera.org/oauth2/v1/token
# def get_access_token():
    
#     access_token = CourseraToken.objects.get(item='access_token')
    
#     if access_token.is_access_token_expired():
#         payload = 'redirect_uri=http%3A%2F%2Flocalhost%3A9876%2Fcallback&client_id=' + COURSERA_CLIENT_ID + '&client_secret=' + COURSERA_CLIENT_SECRET + '&access_type=offline&Content-Type=application%2Fx-www-form-urlencoded&grant_type=refresh_token&refresh_token=' + get_refresh_token_from_django()

#         headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         }

#         response = requests.request("POST", COURSERA_TOKEN_URL, headers=headers, data=payload)
#         response_dict = json.loads(response.text)
#         if 'access_token' in response_dict:
#             new_access_token =  response_dict.get("access_token")
#             access_token = new_access_token
#             try:
#                 access_token_entry = CourseraToken.objects.get(item='access_token')
#             except CourseraToken.DoesNotExist:
#                 access_token_entry = CourseraToken(item='access_token', value=new_access_token)
#                 access_token_entry.save()
#             else:
#                 access_token_entry.value = new_access_token
#                 access_token_entry.save()
        
#         access_token = CourseraToken.objects.get(item='access_token')
    
#     else:
#         print(f'access token: {access_token.value} is modified last {access_token.last_modified} and is not yet expired.')
    
#     return access_token.value

# POST https://api.coursera.org/api/businesses.v1/{{ORG_ID}}/programs/{{PROGRAM_ID}}/invitations
# class InvitationsAPI:
#     def __init__(self, access_token, program_id):
#         self.base_url = DICT_PROGRAMS_URL+"/" + program_id + "/invitations"
#         self.bearer_token = access_token

#     def invite_user(self, external_id, full_name, email, send_email, contract_id=None):
#         params = {}
#         if contract_id:
#             params["contractId"] = contract_id

#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Bearer ' + self.bearer_token
#         }
        
#         payload = json.dumps({
#             "externalId": external_id,
#             "fullName": full_name,
#             "email": email,
#             "sendEmail": send_email
#         })

#         response = requests.request("POST", self.base_url, headers=headers, data=payload, params=params)

#         if response.status_code == 201:
#             return response.json()
#         else:
#             raise Exception(f"Error inviting user: {response.status_code} - {response.text}")

