
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
def home(request):
    return render(request,"index.html")
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        email=request.POST.get("email")
        pass1=request.POST.get("pass1")
        pass2=request.POST.get("pass2")

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')
        
        #if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "username must be under 10 characters")

        if pass1!=pass2:
            messages.error(request, "Password didn't match")

        if not username.isalnum():
            messages.error(request, "user name must be alpha numeric")
            return redirect('home')

        myuser=User.objects.create_user(username, email, pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.is_active=False

        myuser.save()
        messages.success(request,"Your Account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account")

        subject = "welcome to our site"
        message="Hello "+myuser.first_name+"!!\n"+"Welcome to tutorial !! \n Thank you for visiting our website"
        from_email=settings.EMAIL_HOST_USER
        to_list= [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        current_site = get_current_site(request)
        email_subject = "Confirm your email@ GG- django Login!!"
        message2 = render_to_string('email_confirmation.html',{
           'name':myuser.first_name,
           'domain':current_site.domain,
           'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
           'token':generate_token.make_token(myuser)

        })
        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],

        )
        email.fail_silently=True
        email.send()
        return redirect('signin')

    return render(request,"signup.html")
def activate(request, uidb64, token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser= User.objects.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DorsNotExist):
        myuser=None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active=True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')
def signin(request):

    if request.method=='POST':
        username=request.POST.get("username")
        pass1=request.POST.get("pass1")
        print(username)
        print(pass1)
        user=authenticate(username=username, password=pass1)
        #user=User.objects.filter(username=username,password=pass1)
        print(user)
        if user is not None:
            login(request, user)
            fname=user.first_name
            return render(request, "index.html",{'fname':fname})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')
    return render(request,"signin.html")
def signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect('home')
   
