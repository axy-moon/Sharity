from django.shortcuts import render,redirect
from django.contrib.auth.models import auth,User
from .models import *
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import random
import os
from qrcode import *

# Create your views here.

def index(request):
    return render(request,"index.html")

@login_required
def home(request):
    events = Event.objects.order_by('date')
    home_dict = {'event' : events}
    return render(request,"home.html",home_dict)

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

def login_view(request):
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
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

def events(request):
    event = Event.objects.all()
    e = {"events":event}
    return render(request,"events.html",e)

def profile(request):
    return render(request,"profile.html")

def logout_view(request):
    logout(request)
    return redirect('/')


####EVENT MODULE ##########

def create_event(request):
    if request.method == 'POST':
        title = request.POST['event-title']
        subtitle = request.POST['event-subtitle']
        date = request.POST['event-date']
        location = request.POST['event-location']
        desc = request.POST['event-description']
        current_user = request.user
        f = Event.objects.create(event_title=title,event_subtitle=subtitle,location=location,date=date,description=desc,organizer=current_user)
        return redirect('home')
    return render(request,'new_event.html')

def        qr_gen(request,key_id):
    if request.method == 'POST':
        current_user = request.user
        u = User.objects.get(username=current_user)
        e = Event.objects.get(id=key_id)
        data = {'name':u.username,'email':u.email,'event': e.event_title}
        img = make(data)
        img_name = 'qr' + str(u.username) + str(e.event_title) + '.png'
        img_path = os.path.join(settings.MEDIA_ROOT, img_name)
        img.save(img_path)
        recipient = [u.email,]
        from_email = settings.EMAIL_HOST_USER
        subject = 'QR Code for Event - Sharity'
        message = 'Please find your QR code attached below for verifying yourself in the event.'
        email = EmailMessage(subject, message, from_email, recipient)
        email.attach_file(img_path)
        email.send()
        return HttpResponse('Event Registered Successfully')
        
    return redirect('home')