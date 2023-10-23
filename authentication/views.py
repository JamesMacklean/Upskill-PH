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
from .api import InvitationsAPI
from django.core.paginator import Paginator

from .variables import *
import os, requests, ast, jwt, csv

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
                            request.session.modified = True
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
        request.session.modified = True  
    except KeyError:
        pass
    
    return HttpResponse(key, "session data cleared")

def home(request):
    """"""
    template_name = "coursebank/courses.html"
    context = {}

    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "home"
        return render(request, "index.html")
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    # Fetch course data from the API

    context['program_list'] = get_programs(user_token,2,None)
    # context['courses'] = get_courses(request, "static_templates/privacy.html")
    return render(request,template_name, context)
    
# STATIC TEMPLATES
def guidelines(request):
    return render(request, "static_templates/program_guidelines.html")

def privacy(request):
    return render(request, "static_templates/privacy.html")

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
        settings.EMAIL_HOST_USER, 
        ########## ORIGINAL CODE ##########
        [email], 
        ########## FOR TEST CODE ##########
        # [TEST_EMAIL_RECEIVER],
        html_message=html,
        fail_silently=False
    )
    ############################# FOR MAIL ##############################

    return render(request,template_name, context)

def verify_account(request, user_hash):
    """"""
    template_successful = "authentication/verification_successful.html"
    template_failed = "authentication/verification_failed.html"
    context = {}
    
    ########## ANONYMOUS REQUIRED ##########
    if authenticate_user(request):
        return HttpResponseRedirect('/')
    clear_session(request,'url')
    ########## ANONYMOUS REQUIRED ##########

    try:
        email, response_message = verify(user_hash)
                
        if email:
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
        
    try:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']

            user_hash, response_message = create_account(request, email, password)
            context['response_message'] = response_message
            
            if user_hash:
                #### MODAL RESPONSE KUNG NAGWORK BA ANG SIGN UP
                response_message = "success"
                # request.session['user_hash'] = user_hash
                # request.session.modified = True

                print(email, password, user_hash)
                
                ############################# FOR MAIL ##############################
                html = render_to_string('emails/email_verification.html', {
                    'email': email,
                    'user_hash': user_hash,
                    'domain': DOMAIN,
                    'link': API_VERIFY_ACCOUNT_URL
                })
                send_mail(
                    'Title', 
                    'Content of the Message', 
                    settings.EMAIL_HOST_USER, 
                    ########## ORIGINAL CODE ##########
                    [email], 
                    ########## FOR TEST CODE ##########
                    # [TEST_EMAIL_RECEIVER],
                    html_message=html,
                    fail_silently=False
                )
                print(email, password)
                ############################# FOR MAIL ##############################
            
            messages.info(request, response_message)
            
    except Exception as e:
        print(str(e))
    
    return render(request, template_name, context)

def signin(request): 
    """"""
    template_name = "authentication/signin.html"
    context = {}
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user_token, expires, response_message = login_account(username, password)
        
        #### MODAL RESPONSE KUNG NAGWORK BA ANG SIGN IN
        print(response_message)
        
        if user_token:            
            scholarships = user_programs(user_token) 
            partners = user_partners(user_token)
                             
            try:    
                request.session['user_token'] = user_token
                request.session['expires'] = expires
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
                    print('{}: {}'.format(key, value))
                                        
            except jwt.ExpiredSignatureError:
                raise Http404
            
            # context['username'] = username
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
            context['response_message'] = response_message
            return render(request, template_name, context)

    return render(request, template_name, context)

def signout(request):   
    # CLEAR SESSIONS
    try:   
        for key in list(request.session.keys()):
            del request.session[key]
            request.session.modified = True
    except KeyError as e:
        print(str(e))
        
    return redirect('home')

def applied_programs(request):
    """"""
    template_name = "program_dashboard.html"
    context = {}
    applied_programs = []
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "dashboard"
        return HttpResponseRedirect('/signin?next=dashboard')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    scholarships = user_programs(user_token)
            
    if scholarships: 
        try:  
            for data in scholarships:
                program_id = data['program_id']
                applied_programs.append(program_id)
            
        except Exception as e:
            print(str(e))       

    # NAKADEFAULT MUNA ITO SA 2 SINCE DICT PA LANG ANG MAY PROGRAMS
    context['program_list'] = get_programs(user_token,2,None)
    context['profile'] = user_profile(user_token)
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    
    return render(request, template_name, context)

def admin_dashboard(request):
    """"""
    template_name = "admin/admin_dashboard.html"
    context = {}

    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "home"
        return render(request, "index.html")
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    is_staff = request.session['is_staff']
    is_admin = request.session['is_admin']
    is_global = request.session['is_global']
    
    if not (is_global or is_admin or is_staff):
        raise Http404  
    
    user_token = request.session['user_token']
    users = users_list(user_token)
    
    search_term = request.GET.get('search', '')
    filtered_users_set = set()
    
    if search_term:
        for user in users:
            for key, value in user.items():
                if isinstance(value, str) and search_term.lower() in value.lower():
                    filtered_users_set.add(user['id'])  # Add the user's ID to the set
                    break
    else:
        for user in users:
            filtered_users_set.add(user['id'])

    filtered_users = [user for user in users if user['id'] in filtered_users_set]
    
    paginator = Paginator(filtered_users, 50)  # Show 50 users per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if 'generate_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.DictWriter(response, fieldnames=filtered_users[0].keys())
        writer.writeheader()
        for user in filtered_users:
            writer.writerow(user)
        return response
    
    context = {
        'users': page_obj,
        'paginator': paginator,
        'search_query': search_term,  # Add the search query to the context
    }
    return render(request,template_name, context)

def user_details(request, user_id):
    
    template_name = "admin/user_details.html"
    context = {}

    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "home"
        return render(request, "index.html")
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    is_staff = request.session['is_staff']
    is_admin = request.session['is_admin']
    is_global = request.session['is_global']
    
    if not (is_global or is_admin or is_staff):
        raise Http404   
    
    user_token = request.session['user_token']
    profile_details = users_list(user_token, user_id, 'profile')
    education_details = users_list(user_token, user_id, 'education')
    employment_details = users_list(user_token, user_id, 'employment')
    # Add error handling here if needed
    context = {
        'profile_details': profile_details,
        'education_details': education_details,
        'employment_details': employment_details,
    }

    return render(request, template_name, context)

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
    scholarships = user_programs(user_token)
            
    if scholarships: 
        try:  
            for data in scholarships:
                program_id = data['program_id']
                applied_programs.append(program_id)
            
        except Exception as e:
            print(str(e))       

    # NAKADEFAULT MUNA ITO SA 2 SINCE DICT PA LANG ANG MAY PROGRAMS
    context['program_list'] = get_programs(user_token,2,None)
    context['profile'] = user_profile(user_token)
    context['employment'] = user_employment(user_token)
    context['education'] = user_education(user_token)
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    
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

        #### MODAL RESPONSE KUNG NAGWORK BA ANG UPDATE NG PROFILE, EMPLOYMENT AT EDUCATION
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
    context['region_choices'] = REGION
    context['municipality_choices'] = MUNICIPALITIES
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
    
    if request.session['is_partner']:
        user_token = request.session['user_token']
        partners = user_partners(user_token)
        
        if partners:   
            for data in partners:
                partner_id = data['partner_id']
                program_id = data['program_id']
                
                if program_id:
                    programs_list = get_programs(user_token,partner_id,program_id)
                    
                    for program in programs_list:
                        partner_programs.append(program)
    else:
        raise Http404
    
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
    partners = user_partners(user_token)
    
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

        #### MODAL RESPONSE KUNG NAGWORK BA ANG APPLICATION
        print (response_message)
            

    applicants = get_applicants(user_token,partner_id,program_id,None)
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
    applied_programs = []
    status_checker = 0
    ######### LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "program"
        request.session['partner_id'] = partner_id
        request.session['program_id'] = program_id
        return HttpResponseRedirect('/signin?next=program/'+str(partner_id)+"/"+str(program_id)+"/")
    clear_session(request,'url')
    ######### LOGIN REQUIRED ##########
    
    bearer_token = get_access_token()    
    user_token = request.session['user_token']
    username = request.session.get('username')        
    first_name = request.session.get('first_name')
    last_name = request.session.get('last_name')
    email = request.session.get('email')
    user_id = request.session.get('id')
    
    scholarships = user_programs(user_token)
    
    # LOCKED OUT DAPAT ANG OTHER PROGRAMS KAPAG NAGAPPLY SA ISA
    if scholarships:   
        for data in scholarships:
            scholar_program_id = data['program_id']
            applied_programs.append(scholar_program_id)
            status = data['status']
                    
            if status == 1:
                status_checker = status_checker + 1
        
    if request.method == "POST":
        # response = scholar_apply(user_token,program_id)
        license_code = request.POST.get('license_code')
        coursera_program_id = request.POST.get('coursera_program_id')
        full_name = first_name + last_name
        
        access_token = get_access_token()
        api = InvitationsAPI(access_token, coursera_program_id)

        response = enroll_code(user_token, program_id, license_code)
        
        if response == "License Code Verified!":
            invitation_response = api.invite_user(user_id, full_name, email, True)
            print(invitation_response)
            
        #### MODAL RESPONSE KUNG NAGWORK BA ANG APPLICATION
        context['message'] = response
        return render(request, template_name, context)
        
    all_programs = get_programs(user_token, partner_id, None)
    
    for program in all_programs:
        for key, value in program.items():
            if key == 'id':
                program_ids.append(value)
                
    if program_id not in program_ids:
        raise Http404
    
    context['user_details'] = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
    }
    
    context['program_id'] = program_id
    context['programs'] = get_programs(user_token,partner_id,program_id)
    context['dict_programs'] = get_dict_programs(bearer_token)
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    context['atleast_approved_in_a_program'] = status_checker
    
    return render(request, template_name, context)

def certificate(request):
    return render(request, "certificate.html")

def account(request):
    """"""
    template_name = "account.html"
    ########## LOGIN REQUIRED ##########
    if not authenticate_user(request):
        request.session['url'] = "account"
        return HttpResponseRedirect('/signin?next=account')
    clear_session(request,'url')
    ########## LOGIN REQUIRED ##########
    
    user_token = request.session['user_token']
    
    if request.method == "POST":
        current_pass = request.POST.get('current-pass')
        new_pass = request.POST.get('new-pass')
        confirm_pass = request.POST.get('confirm-pass')
    
        if new_pass == confirm_pass:
            response = change_password(user_token, current_pass, new_pass)
            #### MODAL RESPONSE KUNG NAGWORK BA ANG CHANGE PASSWORD
            if response == 'Successfully Updated Password!':
                print (response)
                return redirect ('home')
            else:
                print (response)
                return redirect ('account')
        else:
            #### MODAL RESPONSE KUNG NAGWORK BA ANG CHANGE PASSWORD
            print("password does not match")
            return redirect ('account')
    
    return render(request, template_name)

# def courses(request):
#     """"""
#     template_name = "coursebank/courses.html"
#     context = {}

#     ########## LOGIN REQUIRED ##########
#     if not authenticate_user(request):
#         request.session['url'] = "courses"
#         return HttpResponseRedirect('/signin?next=courses')
#     clear_session(request,'url')
#     ########## LOGIN REQUIRED ##########
    
#     user_token = request.session['user_token']
#     # Fetch course data from the API

    context['program_list'] = get_programs(user_token,2,None)
    context['courses'] = get_courses()
    return render(request,template_name, context)

# STATIC TEMPLATES
def guidelines(request):
    return render(request, "static_templates/program_guidelines.html")

def contact(request):
    return render(request, "static_templates/contact.html")
#     context['program_list'] = get_programs(user_token,2,None)
#     context['courses'] = get_courses()
#     return render(request,template_name, context)
    
# # STATIC TEMPLATES
# def guidelines(request):
#     return render(request, "static_templates/program_guidelines.html")

# def privacy(request):
#     return render(request, "static_templates/privacy.html")

def refresh_token(request):
    """"""
    template_name = "coursera/refresh_token.html"
    context = {}
    
    response = get_refresh_token()
    
    context['response'] = response
    
    return render(request, template_name, context)