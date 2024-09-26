from django.shortcuts import render, redirect
from scholarium import settings
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from scholarium.info import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .api import *
from .forms import *
from .decorators import *
# from .api import InvitationsAPI
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .variables import *
import jwt, csv

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
                    print('{}: {}'.format(key, value), flush=True)    
                return Response(payload)      
                
            except jwt.ExpiredSignatureError:
                # raise AuthenticationFailed('Unauthenticated!')
                raise Http404
            
        except KeyError:
            raise Http404

def clear_session(request,key):
    try:
        del request.session[key]  
        request.session.modified = True  
    except KeyError:
        pass
    
    return HttpResponse(key, "session data cleared")

def home(request):
    """"""
    template_name = "home/home.html"
    context = {}
    applied_programs = []
        
    user_token = request.session['user_token']
    scholarships = user_programs(user_token)
            
    if scholarships: 
        try:  
            for data in scholarships:
                program_id = data['program_id']
                applied_programs.append(program_id)
            
        except Exception as e:
            print(str(e), flush=True)
    
        # TEMP CODE FOR ALL PROGRAMS
    all_programs = []
    
    for i in range(1, 11):
        if i == 6 or i == 9 or i == 10:
            programs = get_programs(user_token, i, None)
            if programs:
                all_programs.extend(programs)
    
    print("ALL PROGRAMS")
    print(all_programs, flush=True)
    
    context['program_list'] = all_programs
    # context['program_list'] = get_programs(user_token, 6,None)
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    # context['courses'] = get_courses(request, "static_templates/privacy.html")
    return render(request,template_name, context)
    
# STATIC TEMPLATES
def guidelines(request):
    return render(request, "static_templates/program_guidelines.html")

def privacy(request):
    return render(request, "static_templates/privacy.html")

def signout(request):   
    # PRINT COOKIES
    for key, value in request.COOKIES.items():
        print(f'{key}: {value}', flush=True)
        
    # CLEAR SESSIONS
    try:   
        for key in list(request.session.keys()):
            del request.session[key]
            request.session.modified = True
    except KeyError as e:
        print(str(e), flush=True)
    
    response = HttpResponseRedirect(reverse('signin'))

    # List of cookies to delete
    cookies_to_delete = [
        '_ups_aut',
    ]

    # Delete cookies
    for cookie in cookies_to_delete:
        response.delete_cookie(cookie)

    return response


def applied_programs(request):
    """"""
    template_name = "program_dashboard.html"
    context = {}
    applied_programs = []
    
    user_token = request.session['user_token']
    scholarships = user_programs(user_token)
            
    if scholarships: 
        try:  
            for data in scholarships:
                program_id = data['program_id']
                applied_programs.append(program_id)
            
        except Exception as e:
            print(str(e), flush=True)       

    # TEMP CODE FOR ALL PROGRAMS
    all_programs = []
    
    for i in range(1, 11):
        if i == 6 or i == 9 or i == 10:
            programs = get_programs(user_token, i, None)
            if programs:
                all_programs.extend(programs)
    
    print("Combined Programs:")
    print(all_programs)
    
    context['program_list'] = all_programs
    # context['program_list'] = get_programs(user_token, 6,None)
    context['profile'] = user_profile(user_token)
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    
    return render(request, template_name, context)

def user_management(request):
    """"""
    template_name = "admin/user_management.html"
    context = {}

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
        'is_staff': is_staff,
        'is_admin': is_admin,
        'is_global': is_global,
        
    }
    return render(request,template_name, context)

def admin_dashboard(request):
    """"""
    template_name = "admin/admin_dashboard.html"
    context = {}

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
        'is_staff': is_staff,
        'is_admin': is_admin,
        'is_global': is_global,
        
    }
    return render(request,template_name, context)

def admin_partners(request, partner_id):
    """"""
    template_name = "admin/admin_partners.html"
    context = {}

    is_staff = request.session['is_staff']
    is_admin = request.session['is_admin']
    is_global = request.session['is_global']
    
    if not (is_global or is_admin or is_staff):
        raise Http404  
    
    user_token = request.session['user_token']
    context['program_list'] = get_programs(user_token,partner_id,None)
    
    return render(request,template_name, context)

def user_details(request, user_id):
    
    template_name = "admin/user_details.html"
    context = {}

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

def license_codes(request, slug):
    template_name = "admin/license_codes.html"
    context = {}

    is_admin = request.session['is_admin']
    is_global = request.session['is_global']
    
    if not (is_global or is_admin):
        raise Http404   
    
    user_token = request.session['user_token']
    program_data = get_program_through_slug(user_token,slug)
    program_id = program_data[0]['id']
    license_codes = license_code(user_token, None)
    program_license_codes = [code for code in license_codes if int(code['program_id']) == int(program_id)]
    
    search_term = request.GET.get('search', '')
    filtered_codes_set = set()
    
    if search_term:
        for code in program_license_codes:
            for key, value in code.items():
                if isinstance(value, str) and search_term.lower() in value.lower():
                    filtered_codes_set.add(code['id'])
                    break
    else:
        for code in program_license_codes:
            filtered_codes_set.add(code['id'])

    filtered_codes = [code for code in program_license_codes if code['id'] in filtered_codes_set]
    
    paginator = Paginator(filtered_codes, 50)  # Show 50 users per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if 'generate_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="license_codes.csv"'

        writer = csv.DictWriter(response, fieldnames=filtered_codes[0].keys())
        writer.writeheader()
        for code in filtered_codes:
            writer.writerow(code)
        return response
    
    # Add error handling here if needed
    context = {
        'license_codes': page_obj,
        'paginator': paginator,
        'search_query': search_term,
    }

    return render(request, template_name, context)

def profile(request):
    """"""
    template_name = "profile_dashboard.html"
    context = {}
    applied_programs = []
    
    user_token = request.session['user_token']
    scholarships = user_programs(user_token)
            
    if scholarships: 
        try:  
            for data in scholarships:
                program_id = data['program_id']
                applied_programs.append(program_id)
            
        except Exception as e:
            print(str(e), flush=True)       

    # TEMP CODE FOR ALL PROGRAMS
    all_programs = []
    
    for i in range(1, 11):
        if i == 6 or i == 9 or i == 10:
            programs = get_programs(user_token, i, None)
            if programs:
                all_programs.extend(programs)
    
    print("Combined Programs:")
    print(all_programs)
    
    context['program_list'] = all_programs
    # context['program_list'] = get_programs(user_token, 6,None)
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
        
    user_token = request.session['user_token']
    
    if request.method == "POST":
        photo = request.POST.get('photo')
        username = request.POST.get('username')
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

        username_update, username_response = update_username(user_token, username)
        profile_update, profile_response = update_profile(user_token, photo, first_name,
                                            last_name, about, country, region, municipality, 
                                            socials, gender, birthday, contact, date_now,privacy)
        employment_update, employment_response = update_employment(user_token, employ_status, industry, 
                                            employer, occupation, exp_level, date_now, privacy)
        education_update, education_response = update_education(user_token, degree, 
                                            university, study, date_now, privacy)

        if username != request.session.get('username'):
            request.session['username']=username
            request.session.modified = True 
            print(f"NEW USERNAME: {username}", flush=True)
        
        if first_name != request.session.get('first_name'):
            request.session['first_name']=first_name
            request.session.modified = True 
            print(f"NEW FIRST NAME: {first_name}", flush=True)
            
        if last_name != request.session.get('last_name'):
            request.session['last_name']=last_name
            request.session.modified = True 
            print(f"NEW LAST NAME: {last_name}", flush=True)

        context['profile'] = profile_update
        context['employment'] = employment_update
        context['education'] = education_update
        
        print(username_update)
        #### MODAL RESPONSE KUNG NAGWORK BA ANG UPDATE NG PROFILE, EMPLOYMENT AT EDUCATION
        print("USERNAME:", username_response, flush=True)
        print("PROFILE:",profile_response, flush=True)
        print("EMPLOYMENT:",employment_response, flush=True)
        print("EDUCATION:",education_response, flush=True)
        
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
    template_name = "partner/partner_selection_page.html"
    user_token = request.session.get('user_token')
    
    if not user_token or not request.session.get('is_partner'):
        raise Http404

    # Get the user's partners (exclude access level==0)
    # partners = user_partners(user_token)
    partners = [p for p in user_partners(user_token) if p.get('access_level') != 0]
    
    if not partners:
        raise Http404
    
    # all_partners = get_partner(user_token)
    all_partners = [p for p in get_partner(user_token) if p.get('status') != 0]
    
    # Collect all unique partner_ids
    # unique_partner_ids = list({data['partner_id'] for data in partners})
    unique_partner_ids = list({
        p['partner_id'] for p in partners
        if any(ap['id'] == p['partner_id'] for ap in all_partners)  # Only include if the partner exists in all_partners with status != 0
    })
    
    if len(unique_partner_ids) == 1:
        # If there is only one unique partner, fetch its details and redirect
        partner_id = unique_partner_ids[0]
        selected_partner = next((partner for partner in all_partners if partner['id'] == partner_id), None)
        
        if not selected_partner or not selected_partner['slug']:
            raise Http404
        
        return HttpResponseRedirect(reverse('partner_slug', kwargs={'partner_slug': selected_partner['slug']}))
    else:
        # If there are multiple unique partners, render the partner selection page
        partner_details = []
        
        for partner_id in unique_partner_ids:
            partner = next((p for p in all_partners if p['id'] == partner_id), None)
            if partner:
                partner_details.append(partner)
        
        context = {
            'partners': partner_details
        }
    return render(request, template_name, context)

def partner_slug(request, partner_slug):
    template_name = "partner/partner_page.html"
    context = {}
    partner_programs = []
    partner_details = []

    user_token = request.session['user_token']
    partners = user_partners(user_token)    
    # Fetch the partner details using the slug
    selected_partner_list = get_partner_through_slug(user_token, partner_slug)
    
    if not selected_partner_list or not isinstance(selected_partner_list, list):
        raise Http404("Partner not found")
    
    selected_partner = selected_partner_list[0]
    partner_details.append(selected_partner)
    
    is_user_partner = False
    if request.session.get('is_partner'):
        if partners:
            # Filter programs associated with the selected partner
            for data in partners:
                if data['partner_id'] == selected_partner['id']:
                    program_id = data['program_id']
                    
                    if program_id:
                        programs_list = get_programs(user_token, selected_partner['id'], program_id)
                        partner_programs.extend(programs_list)
                    if data['access_level'] != 0:
                        is_user_partner = True
    else:
        raise Http404("User is not a partner")
    
    context['partner_details'] = partner_details
    context['program_list'] = partner_programs
    context['is_user_partner'] = is_user_partner

    return render(request, template_name, context)

def partner_edit(request, partner_slug):
    user_token = request.session.get('user_token')
    
    if not request.session.get('is_partner'):
        raise Http404("You are not authorized to edit this partner.")
    
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Fetch the partner using the slug
    selected_partner_list = get_partner_through_slug(user_token, partner_slug)
    
    if not selected_partner_list or not isinstance(selected_partner_list, list):
        raise Http404("Partner not found")
    
    selected_partner = selected_partner_list[0]
    
    if request.method == 'POST':
        
        # Get data from the POST request
        partner_name = request.POST.get('partner_name')
        partner_about = request.POST.get('partner_about')
        partner_slug = request.POST.get('partner_slug')
        partner_url = request.POST.get('partner_url')
        partner_fb = request.POST.get('partner_fb')
        partner_ig = request.POST.get('partner_ig')
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle image uploads
        uploaded_partner_logo_1 = request.FILES.get('partner_logo_1')
        
        # Define a function to save images
        def save_image(uploaded_file, existing_url):
            if uploaded_file:
                file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
                return f'https://{settings.DOMAIN}/static/images/{file_name}'
            return existing_url
        
        partner_logo_cleared = request.POST.get('partner_logo_cleared') == 'true'
        if partner_logo_cleared:
            partner_logo = ""  # Set to empty string if cleared
        else:
            partner_logo = save_image(uploaded_partner_logo_1, selected_partner.get('logo_1'))

        # Call the API to update the partner details
        updated_partner, response_message= update_partner(
            user_token,
            selected_partner['id'],
            partner_logo,
            partner_name,
            partner_about,
            partner_slug,
            partner_url,
            partner_fb,
            partner_ig,
            date_now,
        )
        print(response_message)
        return redirect('partner_slug', partner_slug=partner_slug)
        
    context = {
        'partner': selected_partner
    }
    
    return render(request, 'partner/partner_edit_page.html', context)

def program_slug(request, partner_slug, program_slug):
    template_name = "program/program_page.html"
    context = {}

    user_token = request.session['user_token']
    program_data = get_program_through_slug(user_token, program_slug)
    # Get the user's partners (exclude access level==0)
    # partners = user_partners(user_token)
    partners = [p for p in user_partners(user_token) if p.get('access_level') != 0]
    partner_details = []
    # Get the program using the slug
    
    if not program_data:
        raise Http404
    
    partner_id = program_data[0]['partner_id']
    program_id = program_data[0]['id']        
    
    # monitored_partner = [data['partner_id'] for data in partners]
    # monitored_program = [data['program_id'] for data in partners]
            
    # if partner_id not in monitored_partner:
    #     raise Http404
    # if program_id not in monitored_program:
    #     raise Http404
    
    # Fetch the partner details using the id
    selected_program_list = get_programs(user_token, partner_id,program_id)
    selected_program = selected_program_list[0]

    is_user_partner = False
    if request.session.get('is_partner'):
        if partners:
            for data in partners:
                if data['partner_id'] == selected_program['partner_id']:
                    is_user_partner = True

    else:
        raise Http404("User is not a partner")
    
    context['program_details'] = program_data
    context['partner_slug'] = partner_slug
    context['is_user_partner'] = is_user_partner
    
    if request.method == 'POST':
        csv_data = get_csv_buri(user_token, partner_id, program_id, 0) # status 0 means PENDING
        print(csv_data)
        
        date_now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pending_applications_{date_now}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email Address [Required]', 
            'First Name [Required]', 
            'Last Name [Required]', 
            'Password [Required] atleast 6 characters', 
            'Groups [Required]', 
            'Change password upon login',
            'Confirm account upon upload'
        ])

        for row in csv_data:
            writer.writerow([
                row['email'],
                row['first_name'],
                row['last_name'],
                row['password'],
                row['groups'],
                row['change_pass'],
                row['confirm_account']
            ])

        return response
    
    return render(request, template_name, context)

def program_edit(request, partner_slug, program_slug):
    user_token = request.session.get('user_token')
    
    if not request.session.get('is_partner'):
        raise Http404("You are not authorized to edit this partner.")
    
    selected_partner_list = get_partner_through_slug(user_token, partner_slug)
    selected_program_list = get_program_through_slug (user_token, program_slug)
    
    if not selected_partner_list or not isinstance(selected_partner_list, list):
        raise Http404("Partner not found")
    
    selected_partner = selected_partner_list[0]
    selected_program = selected_program_list[0]
    
    # Ensure date is valid
    def format_date(date_str):
        if date_str and date_str != '0000-00-00 00:00:00':  
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        return ''
    
    selected_program['start_date'] = format_date(selected_program.get('start_date'))
    selected_program['end_date'] = format_date(selected_program.get('end_date'))
    selected_program['registration_end'] = format_date(selected_program.get('registration_end'))
    
    if request.method == 'POST':
        
        # Get data from the POST request        
        program_name = request.POST.get('program_name')
        program_new_slug = request.POST.get('program_slug')
        program_description = request.POST.get('program_description')
        program_about = request.POST.get('program_about')
        program_url = request.POST.get('program_url')
        # program_external_id = request.POST.get('program_external_id')
        program_start_date = request.POST.get('program_start_date')
        program_end_date = request.POST.get('program_end_date')
        program_registration_end = request.POST.get('program_registration_end')
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        program_badge = request.POST.get('program_badge')
        program_certificate = request.POST.get('program_certificate')
        # partner_logo_1 = request.POST.get('partner_logo_1') or selected_program.get('partner_logo_1')
        # partner_logo_2 = request.POST.get('partner_logo_2') or selected_program.get('partner_logo_2')
        # partner_logo_3 = request.POST.get('partner_logo_3') or selected_program.get('partner_logo_3')
        # partner_logo_4 = request.POST.get('partner_logo_4') or selected_program.get('partner_logo_4')
        # image_1 = request.POST.get('program_image_1') or selected_program.get('image_1')
        
        # Handle image uploads
        uploaded_image_1 = request.FILES.get('program_image_1')
        uploaded_logo_1 = request.FILES.get('partner_logo_1')
        uploaded_logo_2 = request.FILES.get('partner_logo_2')
        uploaded_logo_3 = request.FILES.get('partner_logo_3')
        uploaded_logo_4 = request.FILES.get('partner_logo_4')
        
        # Define a function to save images
        def save_image(uploaded_file, existing_url):
            if uploaded_file:
                file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
                return f'https://{settings.DOMAIN}/static/images/{file_name}'
            return existing_url
        
        program_image_cleared = request.POST.get('program_image_cleared') == 'true'
        if program_image_cleared:
            image_1 = ""  # Set to empty string if cleared
        else:
            image_1 = save_image(uploaded_image_1, selected_program.get('image_1'))
        partner_logo_1_cleared = request.POST.get('partner_logo_1_cleared') == 'true'
        if partner_logo_1_cleared:
            partner_logo_1 = ""  # Set to empty string if cleared
        else:
            partner_logo_1 = save_image(uploaded_logo_1, selected_program.get('partner_logo_1'))
        
        partner_logo_2_cleared = request.POST.get('partner_logo_2_cleared') == 'true'
        if partner_logo_2_cleared:
            partner_logo_2 = ""  # Set to empty string if cleared
        else:
            partner_logo_2 = save_image(uploaded_logo_2, selected_program.get('partner_logo_2'))

        partner_logo_3_cleared = request.POST.get('partner_logo_3_cleared') == 'true'
        if partner_logo_3_cleared:
            partner_logo_3 = ""  # Set to empty string if cleared
        else:
            partner_logo_3 = save_image(uploaded_logo_3, selected_program.get('partner_logo_3'))

        partner_logo_4_cleared = request.POST.get('partner_logo_4_cleared') == 'true'
        if partner_logo_4_cleared:
            partner_logo_4 = ""  # Set to empty string if cleared
        else:
            partner_logo_4 = save_image(uploaded_logo_4, selected_program.get('partner_logo_4'))
        
        # Call the API to update the program details
        updated_program, response_message= update_program(
            user_token,
            selected_program['id'],
            selected_partner['id'],
            program_name,
            program_new_slug,
            program_url,
            program_description,
            program_about,
            program_start_date,
            program_registration_end,
            program_end_date,
            date_now,
            program_badge,
            program_certificate,
            partner_logo_1,
            partner_logo_2,
            partner_logo_3,
            partner_logo_4,
            image_1,"","","" # images
        )
        
        print(updated_program)
        print(response_message)
        return redirect('program_slug', partner_slug=partner_slug, program_slug = program_new_slug)
        
    context = {
        'partner': selected_partner,
        'program': selected_program
    }
    
    return render(request, 'program/program_edit_page.html', context)

# ADD/EDIT CERTIFICATE

# def edit_certificate():
#     """"""

# CERTIFICATE PREVIEW
# def preview_certificate(request):
#     """"""
#     template_name = "certificate/certificate.html"

#     return render(request, template_name)

def application(request, partner_slug, program_slug):
    """"""
    template_name = "scholar_application.html"
    context = {}
    scholarship_applicants = []
        
    user_token = request.session['user_token']
    # Get the user's partners (exclude access level==0)
    partners = [p for p in user_partners(user_token) if p.get('access_level') != 0]
    
    # Get the program using the slug
    program_data = get_program_through_slug(user_token, program_slug)
    if not program_data:
        raise Http404
    
    partner_id = program_data[0]['partner_id']
    program_id = program_data[0]['id']
    
    monitored_partner = [data['partner_id'] for data in partners]
    monitored_program = [data['program_id'] for data in partners]
            
    if partner_id not in monitored_partner:
        raise Http404
    if program_id not in monitored_program:
        raise Http404
        
    if request.method == "POST":
        user_ids = request.POST.getlist("user_id[]")

        response_message = ''
        applicants = get_applicants(user_token,partner_id,program_id,None)
        for applicant in applicants:
            scholarship_applicants.append(applicant)
            
        for user_id in user_ids:
            for applicant in scholarship_applicants:
                if str(applicant['user_id']) == user_id:
                    applicant_name = f"{applicant['first_name']} {applicant['last_name']}"
                    applicant_email = applicant['email']
                    
            if 'approve' in request.POST:
                print("APPROVE attempt", flush=True)
                response_message = update_applicant(user_token, int(user_id), int(partner_id), int(program_id), 1)
                if response_message == "Successfully Updated!":
                    csv_data = get_csv_buri(user_token, partner_id, program_id, 1) # status 1 means APPROVED
                    print(csv_data)
                    
                    applicant_password = None
                    for record in csv_data:
                        if record['email'] == applicant_email:
                            applicant_password = record['password']  # Get the password from the CSV data
                            break
                    if applicant_password:
                        print(applicant_password, flush = True)
                        ############################# FOR MAIL ##############################
                        html = render_to_string('emails/lakip_approval.html', {
                            'email': applicant_email,
                            'full_name': applicant_name,
                            'password': applicant_password,
                            ########## ORIGINAL CODE ##########
                            'domain': "dict-lakip.upskillph.org" 
                        })
                        try:
                            send_mail(
                                'Application Approved', 
                                '', 
                                settings.EMAIL_HOST_USER, 
                                ########## ORIGINAL CODE ##########
                                [applicant_email], 
                                ########## FOR TEST CODE ##########
                                # [TEST_EMAIL_RECEIVER],
                                html_message=html,
                                fail_silently=False
                            )
                            print(f'Approval email sent to {applicant_email}', flush=True)
                        except Exception as e:
                            print("Failed to send email:", str(e), flush=True)
                        ############################# FOR MAIL ##############################
                    else:
                        print(f"Password for {applicant_email} not found in csv_data.", flush=True)
                else:
                    response_message == "Approval Failed."

            elif 'waitlist' in request.POST:
                print("WAITLIST attempt", flush=True)
                response_message = update_applicant(user_token, int(user_id), int(partner_id), int(program_id), 2)
            elif 'reject' in request.POST:
                print("REJECT attempt", flush=True)
                response_message = update_applicant(user_token, int(user_id), int(partner_id), int(program_id), 3)
            elif 'clear' in request.POST:
                print("CLEAR attempt", flush=True)
                response_message = update_applicant(user_token, int(user_id), int(partner_id), int(program_id), 0)

            print(f'APPLICATION: {response_message} for user_id: {user_id}', flush=True)

    applicants = get_applicants(user_token,partner_id,program_id,None)
    scholarship_applicants = []
    for applicant in applicants:
        scholarship_applicants.append(applicant)
        
    context['programs'] = program_data
    context['scholarship_applicants'] = scholarship_applicants
    context[partner_slug] = partner_slug
    
    return render(request, template_name, context)

def program(request, slug):
    """"""
    template_name = "scholar_programs.html"
    context = {}
    program_ids = []
    applied_programs = []
    user_program = []
    status_checker = 0
    
    # bearer_token = get_access_token()  
    user_token = request.session['user_token']  
    username = request.session.get('username')        
    first_name = request.session.get('first_name')
    last_name = request.session.get('last_name')
    email = request.session.get('email')
    user_id = request.session.get('id')
    
    scholarships = user_programs(user_token)
    program_data = get_program_through_slug(user_token,slug)
    program_id = 0
    
    # LOCKED OUT DAPAT ANG OTHER PROGRAMS KAPAG NAGAPPLY SA ISA
    # I-CHECK LAHAT NG SCHOLARSHIP NI USER
    if scholarships:
        # ILAGAY SA 'APPLIED PROGRAMS' LAHAT NG PROGRAM ID NG SCHOLARSHIP NI USER
        for data in scholarships:
            scholar_program_id = data['program_id']
            applied_programs.append(scholar_program_id)
            status = data['status']
            if status == 1:
                status_checker = status_checker + 1
        
    # KUNIN ANG PROGRAM ID NG CINLICK NA PROGRAM
    for data in program_data:
        program_id = data['id']

    # ILAGAY SA 'USER_PROGRAM' ANG SCHOLARSHIP DETAILS NI USER ABOUT SA PROGRAM NA ITO
    for scholarship in scholarships:
        if scholarship['program_id'] == program_id:
            user_program.append(scholarship)
    
    if request.method == "POST":
        # license_code = request.POST.get('license_code')
        full_name = first_name + last_name
        # coursera_program_id = request.POST.get('coursera_program_id')
         
        # access_token = get_access_token()
        # api = InvitationsAPI(access_token, coursera_program_id)

        # response = enroll_code(user_token, program_id, license_code)
        response = enroll_program(user_token, program_id)
        
        # if response == "License Code Verified!":
            # invitation_response = api.invite_user(user_id, full_name, email, True)
            # print(invitation_response)
            
        #### MODAL RESPONSE KUNG NAGWORK BA ANG APPLICATION
        context['message'] = response
        return render(request, template_name, context)
    
    # TEMP CODE FOR ALL PROGRAMS
    all_programs = []
    
    for i in range(1, 11):
        if i == 6 or i == 9 or i == 10:
            programs = get_programs(user_token, i, None)
            if programs:
                all_programs.extend(programs)
    
    print("Combined Programs:")
    print(all_programs)
    
    # KUNIN LAHAT NG DATA NG MGA PROGRAMS
    # all_programs = get_programs(user_token, 6, None)

    for program in all_programs:
        for key, value in program.items():
            if key == 'id':
                program_ids.append(value)

    # 404 ERROR KAPAG WALA SA LISTAHAN NG PROGRAM IDS ANG PROGRAM NA CINLICK    
    if program_id not in program_ids:
        raise Http404
    
    context['user_details'] = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
    }
    
    context['program_slug'] = slug
    context['programs'] = program_data
    context['user_program'] = user_program
    context['scholarships'] = scholarships
    context['applied_programs'] = applied_programs
    context['atleast_approved_in_a_program'] = status_checker
    
    return render(request, template_name, context)

def certificate(request):
    return render(request, "certificate.html")

def account(request):
    """"""
    template_name = "account.html"
    context = {}
    response = ""
    user_token = request.session['user_token']
    
    if request.method == "POST":
        current_pass = request.POST.get('current-pass')
        new_pass = request.POST.get('new-pass')
        confirm_pass = request.POST.get('confirm-pass')
    
        if new_pass == confirm_pass:
            response = change_password(user_token, current_pass, new_pass)
        else:
            response = "Password does not match"
    
    print(response, flush=True)
    context['response_message'] = response
    
    return render(request, template_name, context)

def lakip_landing(request):
    """"""
    template_name="lakip-landing.html"

    return render(request, template_name)

def lakip_application(request):
    """"""
    template_name= "lakip-application.html"

    return render(request, template_name)


# def courses(request):
#     """"""
#     template_name = "home/courses.html"
#     context = {}

#     user_token = request.session['user_token']
#     # Fetch course data from the API

#    context['program_list'] = get_programs(user_token,2,None)
#    context['courses'] = get_courses()
#    return render(request,template_name, context)

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

# def refresh_token(request):
#     """"""
#     template_name = "coursera/refresh_token.html"
#     context = {}
    
#     response = get_refresh_token()
    
#     context['response'] = response
    
#     return render(request, template_name, context)