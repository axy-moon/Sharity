from django.shortcuts import render,redirect
from django.contrib.auth.models import auth,User
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import random

# Create your views here.

def index(request):
    return render(request,"index.html")

def home(request):
    return render(request,"home.html")

def register(request):
    global uemail,username
    if request.method == "POST":
        username = request.POST['username']
        uemail = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if(password==cpassword):
            User.objects.create_user(username=username,email=uemail,password=password)
            return redirect('verify')
        else:
            return HttpResponse("Password doesn't match")
        
    else:
        return render(request,"register.html")

def login(request):
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']
        u = authenticate(username=username, password=password)
        if u is not None:
            return redirect('home')
        else:
            return HttpResponse("Invalid User")
    return render(request,"login.html")

def verify(request):
    global otp
    if(request.method == 'POST'):
        entered_otp = request.POST['otp']
        print(otp)
        if (int(entered_otp)==int(otp)):
            return redirect('login')
        else:
            d = User.objects.latest()
            d.delete()
            return HttpResponse("failed")
    otp = random.randrange(1000,9999)
    print(username,uemail,otp)
    mail_verify(username,uemail,otp)
    print(otp)
    return render(request,"verify.html")


def mail_verify(username,email,otp):
    subject = '' + str(otp)
    message = f'Hi {username}, Welcome to Sharity. Your OTP for verifying your account is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail( subject, message, email_from, recipient_list )
    return True

