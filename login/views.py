from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate ,login

import login

# Create your views here.
def home(request):
    return render(request, "index.html")

def success(request):
    return render(request, "welcome.html")

def signup(request):

    if request.method == "POST":
        dusername = request.POST['username']
        dfirstname = request.POST['firstname']
        dlastname = request.POST['lastname']
        demail = request.POST['email']

        dmyuser = User.objects.create_user(dusername, demail)
        dmyuser.first_name = dfirstname
        dmyuser.last_name = dlastname

        dmyuser.save()

        messages.success(request, "Your Account has been successfully created!")
        
        return redirect('welcome')

    return render(request, "authentication/login.html")

def signin(request):
    if request.method == "POST":
        dusername = request.POST['username']
        dpassword = request.POST['password']

        user = authenticate(username=dusername, password=dpassword)

        if user is not None:
            login(request, user)
            firstname = user.firstname
            return render(request, "authentication/dashboard.html",{'firstname': firstname})

        else:
            messages.error(request,"Invalid Username/Password")
            return redirect('home')

    return render(request, "authentication/login.html")