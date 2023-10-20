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
import PyPDF2
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch,Pinecone,Weaviate,FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

# Create your views here.

def index(request):
    return render(request,"index.html")

@login_required
def details(request):
    if request.method == "POST":
        fname = request.POST['fName']
        lname = request.POST['lName']
        age = request.POST['age']
        gender = request.POST['gender']
        city = request.POST['city']
        role = request.POST['radio1']
        idproof = request.FILES['id-proof']

        user = User.objects.get(username=request.user)
        user.first_name = fname
        user.last_name = lname
        user.save()
        Profile.objects.create(name=user,age=age,gender=gender,location=city,role=role,id_proof=idproof)
        print(fname,lname,age,gender,city,role)
        return redirect("home")
        
    return render(request,"userdetails.html")

@login_required
def home(request):
    events = Event.objects.order_by('date')
    home_dict = {'event' : events}
    print(settings.BASE_DIR)
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
    invalid = False
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
           if user.last_login:
                auth.login(request,user)
                return redirect('home')
           else:
                auth.login(request,user)
                return redirect('details')
        else:
            invalid = True
            return render(request,"login.html",locals())
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
    searching = False
    if request.method=='POST':
        keyword=request.POST.get('search')
        search_events=Event.objects.filter(event_title__icontains=keyword)
        searching = True

        context={
            'result':search_events,
            'boolean':searching,
            'keyword':keyword 
        }

        print(context)
        return render(request,'events.html',context)
    event = Event.objects.all()
    e = {"events":event}
    return render(request,"events.html",e)

def profile(request):
    data = Event.objects.all()
    temp = {"data" : data}
    return render(request,"profile.html",temp)

def category(request):
    success()
    return render(request,"category.html")

def logout_view(request):
    logout(request)
    return redirect('/')

def feeds(request):
    if request.method == "POST":
        tags = []
        content = request.POST['postContent']
        post_image = request.FILES['file']
        
        Post.objects.create(author=request.user,content=content,img=post_image)
        return redirect('feeds')
    all_posts = Post.objects.all()
    return render(request,"feeds.html",{ "posts": all_posts })


####EVENT MODULE ##########

def create_event(request):
    if request.method == 'POST':
        title = request.POST['event-title']
        subtitle = request.POST['event-subtitle']
        date = request.POST['event-date']
        time = request.POST['time']
        location = request.POST['event-location']
        desc = request.POST['event-description']
        category = request.POST['category']

        current_user = request.user
        f = Event.objects.create(event_title=title,event_subtitle=subtitle,location=location,date=date,description=desc,organizer=current_user,time=time)
        return redirect('home')
    return render(request,'new_event.html')

def qr_gen(request,key_id):
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
    return render(request,"home.html",{"toast":True})
        

def event_details(request,key_id):
    info = Event.objects.get(id=key_id)
    data = { "event" : info }
    return render(request,"event_details.html",data)

def nearby(request):
    return render(request,"nearby.html")


def success():
    global raw_text
    raw_text=''
    filepath = os.path.join(settings.BASE_DIR,'community/static/traindata')
    for filename in os.listdir(filepath):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(filepath, filename)
            raw_text += read_pdf(pdf_path)
    print(raw_text)
    #return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


def read_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    

def chatbot(request):

    print("chat called")
    if request.method == "POST":
        question=request.POST['text']
        os.environ["OPENAI_API_KEY"]="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"
        text_splitter=CharacterTextSplitter(
        separator="\n",
        chunk_size=10000,
        chunk_overlap=200,
        length_function=len
        )
        texts=text_splitter.split_text(raw_text)
        embeddings=OpenAIEmbeddings()
        docsearch = FAISS.from_texts(texts,embeddings)
        chain=load_qa_chain(OpenAI(),chain_type="stuff")
        #query="does the author have any work experience?"
        docs=docsearch.similarity_search(question)
        return HttpResponse(chain.run(input_documents=docs,question=question))
