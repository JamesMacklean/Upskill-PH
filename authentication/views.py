from email.message import EmailMessage
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from scholarium import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token


import authentication
# Create your views here.

def home(request):
    return render(request,"index.html")

def success(request):
    return render(request,"welcome.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        email= request.POST['email']
        firstname= request.POST['firstname']
        lastname= request.POST['lastname']

        if User.objects.filter(username=username):
            messages.error(request, "username already exists")
        
        if User.objects.filter(email=email):
            messages.error(request, "email already exists")

        
        myuser = User.objects.create_user(username, email, firstname, lastname)
        myuser.is_active = False
        myuser.save()

        current_site = get_current_site(request)
        subject = "Scholarium: Account Verification"
        message = render_to_string('email_confirmation.html',{
            'name': myuser.firstname,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('success')

    return render(request, "authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            first_name = user.firstname
            return render(request, "authentication/dashboard.html", {'first_name': first_name})

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

def profile(request):
    return render(request, "profile.html")

def edit_profile(request):
    return(request, "edit_profile.html")
