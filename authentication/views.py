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
from .forms import *
from .decorators import *
from django.template import Library

from .variables import *
import os, requests, ast, jwt
import json
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
        # PRINT SESSION ITEMS
        for key, value in request.session.items():
            print('{}: {}'.format(key, value))
                 
        try:   
            user_token = request.session['user_token'] 
            payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])

            # SAVE JWT PAYLOAD INTO SESSIONS
            for key,value in payload.items():
                if key == 'data':
                    for key,value in payload['data'].items():
                        # if request.session['first_name'] or request.session['last_name']:
                        if request.session[key]:
                            pass
                        else:
                            request.session[key] = value
                            
            request.session.modified = True
            return True
        
        except jwt.ExpiredSignatureError:
            signout(request)
            return False
        
    except KeyError:
        signout(request)
        return False
    
def clear_session(request,key):
    try:
        del request.session[key]    
    except KeyError:
        pass
    
    return HttpResponse(key, "session data cleared")

def home(request):
    """"""
    template_anonymous = "authentication/signin.html"
    template_authenticated = "authentication/dashboard.html"
    context = {}
    
    ########## LOGIN REQUIRED ##########
    if authenticate_user(request):
        return render(request, template_authenticated, context)
    ########## LOGIN REQUIRED ##########

    ###################### https://scholarium.tmtg-clone.click/api/login ######################
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
    ###################### https://scholarium.tmtg-clone.click/api/login ######################
        
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user_token, expires, response_message = login_account(username, password)
        
        if user_token:
            # PUT JWT TOKEN TO COOKIES
            # response = Response()
            # response.set_cookie(key='jwt',value=user_token, httponly=True)
            # response.data = {
            #     'jwt': user_token
            # }
            
            # print('COOKIE RESPONSE:', response.data)
            
            try:    
                request.session['user_token'] = user_token
                request.session['expires'] = expires
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
                raise Http404
            
            context['username'] = username
            context['expires'] = expires
            context['user_token'] = user_token
            
            # CHECK IF THE REQUEST IS REDIRECTION
            try:
                next_page = request.session.get('url')
            except:
                next_page = ""
            
            # IF REDIRECTION SIYA, PUNTA SA NEXT PAGE, PERO KUNG HINDI, SA DASHBOARD
            if next_page:
                try:
                    if next_page == 'application' or next_page == 'program':
                        partner_id = request.session.get('partner_id')
                        program_id = request.session.get('program_id')
                        clear_session(request,'partner_id')
                        clear_session(request,'program_id')
                        return HttpResponseRedirect(reverse(next_page,kwargs={'partner_id':partner_id,'program_id':program_id}))

                    return HttpResponseRedirect(reverse(next_page))
            
                except Exception as e:
                    print(str(e))
            
            else:
                return redirect('home')

        else:
            # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
            print ("ERROR:", response_message)
            # return render(request, template_name, context)

    # return render(request, template_name, context)
    return render(request,template_anonymous, context)

def success(request, user_hash):
    """"""
    template_name = "success.html"
    context = {}

    username = request.session.get('new_username')        
    first_name = request.session.get('new_first_name')
    last_name = request.session.get('new_last_name')
    email = request.session.get('new_email')
    
    ########## ANONYMOUS REQUIRED ##########
    if authenticate_user(request):
        return HttpResponseRedirect('/')
    clear_session(request,'url')
    ########## ANONYMOUS REQUIRED ##########

    ############################# FOR MAIL ##############################
    html = render_to_string('emails/email_verification.html', {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'user_hash': user_hash,
        'domain': DOMAIN,
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
    
    context['email'] = email
    
    return render(request,template_name, context)

def verify_account(request, user_hash):
    """"""
    template_successful = "authentication/verification_successful.html"
    template_failed = "authentication/verification_failed.html"
    context = {}
    
    ###################### https://scholarium.tmtg-clone.click/api/user/verify/[args] ###################### 
    def verify(user_hash):
        payload={}
        files={}
        headers = {
        'Authorization': API_TOKEN
        }
        response = requests.request("PUT", os.path.join(API_VERIFY_ACCOUNT_URL, user_hash), headers=headers, data=payload, files=files)
        response_dict = ast.literal_eval(response.text)
    ###################### https://scholarium.tmtg-clone.click/api/user/verify/[args] ###################### 
         
        if 'data' in response_dict:
            for data in response_dict['data']:
                response_message = data.get("success")
                password = data.get("password")
        else:
            response_message = response_dict.get("error")
            password=''   
        
        return password,response_message
    
    try:
        password, response_message = verify(user_hash)
        
        context['response_message'] = response_message
        context['password'] = password
        context['domain'] = DOMAIN
        
        if password != '':
            print ("SUCCESS:", response_message)
            return render(request, template_successful, context)                 
        else:
            print ("ERROR:", response_message)
            return render(request, template_failed, context) 
        
    except Exception as e:
        print(str(e))
        return render(request, template_failed, context)
    
def signup(request):
    """"""
    template_name = "authentication/signup.html"
    context = {}

    ###################### https://scholarium.tmtg-clone.click/api/user/create ###################### 
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
    ###################### https://scholarium.tmtg-clone.click/api/user/create ###################### 
        
    try:
        if request.method == "POST":
            username = request.POST['username']
            email= request.POST['email']
            firstname= request.POST['firstname']
            lastname= request.POST['lastname']

            user_hash, response_message = create_account(username,firstname,lastname,email)
            
            if user_hash:
                context['message'] = "success"
                request.session['user_hash'] = user_hash
                return redirect('success', user_hash)
            else:
                context['message'] = response_message
                return render(request, template_name, context)

        return render(request, template_name, context)
    
    except Exception as e:
        print(str(e))
        return render(request, template_name, context)
    
def signin(request): 
    """"""
    template_name = "authentication/signin.html"
    context = {}
    
    ###################### https://scholarium.tmtg-clone.click/api/login ######################
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
    ###################### https://scholarium.tmtg-clone.click/api/login ######################
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user_token, expires, response_message = login_account(username, password)
        
        if user_token:
            # PUT JWT TOKEN TO COOKIES
            # response = Response()
            # response.set_cookie(key='jwt',value=user_token, httponly=True)
            # response.data = {
            #     'jwt': user_token
            # }
            
            # print('COOKIE RESPONSE:', response.data)
            
            try:    
                request.session['user_token'] = user_token
                request.session['expires'] = expires
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
                raise Http404
            
            context['username'] = username
            context['expires'] = expires
            context['user_token'] = user_token
            
            # CHECK IF THE REQUEST IS REDIRECTION
            try:
                next_page = request.session.get('url')
            except:
                next_page = ""
            
            # IF REDIRECTION SIYA, PUNTA SA NEXT PAGE, PERO KUNG HINDI, SA DASHBOARD
            if next_page:
                try:
                    if next_page == 'application' or next_page == 'program':
                        partner_id = request.session.get('partner_id')
                        program_id = request.session.get('program_id')
                        clear_session(request,'partner_id')
                        clear_session(request,'program_id')
                        return HttpResponseRedirect(reverse(next_page,kwargs={'partner_id':partner_id,'program_id':program_id}))

                    return HttpResponseRedirect(reverse(next_page))
            
                except Exception as e:
                    print(str(e))
            
            else:
                return redirect('home')

        else:
            # LAGYAN ITO NG MESSAGE BOX NA NAGSASABI NG ERROR MESSAGE
            print ("ERROR:", response_message)
            return render(request, template_name, context)

    return render(request, template_name, context)

def signout(request):   
    # CLEAR SESSIONS
    try:   
        for key in list(request.session.keys()):
            del request.session[key]
    except KeyError as e:
        print(str(e))
        
    return redirect('home')

def profile(request):
    """"""
    template_name = "profile_dashboard.html"
    context = {}
    applied_programs = []
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "profile"
        return HttpResponseRedirect('/signin?next=profile')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    # IRERESTRUCTURE ITO PANG-GET
    scholarships = request.session['scholarships']
    
    if scholarships:   
        for data in scholarships:
            program_id = data['program_id']
            applied_programs.append(program_id)
    
    print (applied_programs)
    context['applied_programs'] = applied_programs
    # NAKADEFAULT MUNA ITO SA 2 SINCE DICT PA LANG ANG MAY PROGRAMS
    context['program_list'] = get_programs(user_token,2,None)
    context['profile'] = user_profile(user_token)
    context['employment'] = user_employment(user_token)
    context['education'] = user_education(user_token)
    
    return render(request, template_name, context)

def edit_profile(request):
    """"""
    template_name = "edit_profile.html"
    context = {}
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "edit"
        return HttpResponseRedirect('/signin?next=edit')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    if request.method == "POST":
        photo = request.POST.get('photo')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        employ_status = request.POST.get('employ_status')
        industry = request.POST.get('industry')
        employer = request.POST.get('employer')
        occupation = request.POST.get('occupation')
        exp_level = request.POST.get('exp_level')
        degree = request.POST.get('degree')
        university = request.POST.get('university')
        study = request.POST.get('study')
        about = request.POST.get('bio')
        country = request.POST.get('country')
        region = request.POST.get('region')
        municipality = request.POST.get('municipality')
        socials = request.POST.get('socials')
        gender = request.POST.get('gender')
        birthday = request.POST.get('birthday')
        contact = request.POST.get('mobile')
        privacy = request.POST.get('details_privacy')
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        request.session['first_name']=first_name
        request.session['last_name']=last_name
        request.session.modified = True 

        profile_update, profile_response = update_profile(user_token, photo, first_name,
                                            last_name, about, country, region, municipality, 
                                            socials, gender, birthday, contact, date_now,privacy)
        employment_update, employment_response = update_employment(user_token, employ_status, industry, 
                                            employer, occupation, exp_level, date_now, privacy)
        education_update, education_response = update_education(user_token, degree, 
                                            university, study, date_now, privacy)
        
        context['profile'] = profile_update
        context['employment'] = employment_update
        context['education'] = education_update

        print("PROFILE:",profile_response)
        print("EMPLOYMENT:",employment_response)
        print("EDUCATION:",education_response)
        
        return redirect("profile")

    context['profile'] = user_profile(user_token)
    context['employment'] = user_employment(user_token)
    context['education'] = user_education(user_token)
    
    # LIST POPULATOR    
    context['employment_status_choices'] = EMPLOYMENT_STATUS
    context['industry_choices'] = INDUSTRY
    context['experience_choices'] = EXPERIENCE
    context['degree_choices'] = DEGREE
    context['field_of_study_choices'] = FIELD_OF_STUDY
    context['country_choices'] = COUNTRY
    context['gender_choices'] = GENDER
    
    return render(request, template_name, context)

def partner(request):
    """"""
    template_name = "partner_dashboard.html"
    context = {}
    partner_programs = []
    
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "partner"
        return HttpResponseRedirect('/signin?next=partner')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    # IRERESTRUCTURE ITO PANG-GET
    partners = request.session['partners']
    
    if partners:   
        for data in partners:
            partner_id = data['partner_id']
            program_id = data['program_id']
            programs_list = get_programs(user_token,partner_id,program_id)
            
            for program in programs_list:
                partner_programs.append(program)

    context['program_list'] = partner_programs
    
    return render(request, template_name, context)

def application(request, partner_id, program_id):
    """"""
    template_name = "scholar_application.html"
    context = {}
    scholarship_applicants = []
    monitored_partner = []
    monitored_program = []
    
    ######### LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "application"
        request.session['partner_id'] = partner_id
        request.session['program_id'] = program_id
        return HttpResponseRedirect('/signin?next=application/'+str(partner_id)+"/"+str(program_id)+"/")
    clear_session(request,'url')
    ######### LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    # IRERESTRUCTURE ITO PANG-GET
    partners = request.session['partners']
    
    for data in partners:
            monitored_partner.append(data['partner_id'])
            monitored_program.append(data['program_id'])
            
    if partner_id not in monitored_partner:
        raise Http404
    if program_id not in monitored_program:
        raise Http404

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        request_program_id = request.POST.get("program_id")
        
        if 'approve' in request.POST:
            response_message = update_applicant(user_token, user_id, request_program_id, 1)
        elif 'waitlist' in request.POST:
            response_message = update_applicant(user_token, user_id, request_program_id, 2)
        elif 'reject' in request.POST:
            response_message = update_applicant(user_token, user_id, request_program_id, 3)

        print(response_message)

    applicants = get_applicants(user_token,program_id,None)
    
    for applicant in applicants:
        scholarship_applicants.append(applicant)

    context['programs'] = get_programs(user_token,partner_id,program_id)
    context['scholarship_applicants'] = scholarship_applicants
    
    return render(request, template_name, context)

def program(request, partner_id, program_id):
    """"""
    template_name = "scholar_programs.html"
    context = {}
    program_ids = []
    
    ######### LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "program"
        request.session['partner_id'] = partner_id
        request.session['program_id'] = program_id
        return HttpResponseRedirect('/signin?next=program/'+str(partner_id)+"/"+str(program_id)+"/")
    clear_session(request,'url')
    ######### LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    ###################### https://scholarium.tmtg-clone.click/api/me/scholarship ######################
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
    ###################### https://scholarium.tmtg-clone.click/api/me/scholarship ######################
    
    if request.method == "POST":
        response = scholar_apply(user_token,program_id)
        print(response)
    
    all_programs = get_programs(user_token, partner_id, None)
    
    for program in all_programs:
        for key, value in program.items():
            if key == 'id':
                program_ids.append(value)
                
    if program_id not in program_ids:
        raise Http404
    
    context['programs'] = get_programs(user_token,partner_id,program_id)
    
    return render(request, template_name, context)

def certificate(request):
    return render(request, "certificate.html")

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
