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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .decorators import *


import authentication
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

        if User.objects.filter(username=username):
            messages.error(request, "username already exists")
        
        if User.objects.filter(email=email):
            messages.error(request, "email already exists")
        
        messages.success(request,"account created successfully")
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.save()

        Profile.objects.create(
            user = myuser,
            fname = myuser.first_name,
            lname = myuser.last_name
        )

        return redirect('signup')

    return render(request, "authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, "authentication/dashboard.html")

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

@login_required(login_url='signin')
def profile(request):
    user = request.user

    program = Program.objects.filter(is_active=True)
    available = []
    ongoing = []

    for group in program.groups.all().filter(is_active=True):
        programs = {}
        if group.type == "AB":
            available.append(programs)
        else:
            ongoing.append(programs)

    form = ProfileForm(instance=user)
    context = {
        'form':form,
        'program':program,
    }
    return render(request, "profile.html",context)

@login_required(login_url='signin')
def partner(request):
    return render(request, "partner_dashboard.html")

@login_required(login_url='signin')
def edit_profile(request):
    user = request.user
    form = ProfileForm(instance=user)
    context = {'form':form}

    return render(request, "edit_profile.html", context)

@login_required(login_url='signin')
def program(request, slug):
    """"""
    template_name = "scholar_program.html"
    context = {}

    program = get_object_or_404(Program, slug=slug)
    
    context['program']= program
    context['partner_logos']= Program.objects.partner_logo
    return render(request, template_name, context)
