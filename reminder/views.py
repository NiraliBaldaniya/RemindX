from django.shortcuts import render,redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import EmailOTP,Task
from secrets import randbelow
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password,check_password
from django.core.mail import send_mail
import re
from django.contrib.auth import get_user_model, login as auth_login,logout
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required

@login_required(login_url='/')
def home(request):
    email = request.user.email

    name = email.split("@")[0] if email else "Remindian"
    name = re.sub(r'\d+$', '', name)

    tasks = Task.objects.filter(user=request.user).order_by('date', 'time')

    return render(request, 'index.html', {'name': name, 'tasks' : tasks })


def login(request):
    return render(request,'registration/login.html')


def user_logout(request):
    logout(request)
    return redirect('/')


@require_POST
def email_login(request):

    email = request.POST.get('email')

    if not email:
        return JsonResponse({
            'error': 'Email is required'
        }, status=400)

    otp = str(randbelow(900000) + 100000)

    expires_at = timezone.now() + timedelta(minutes=20)

    otp_record = EmailOTP.objects.create(
        email=email,
        otp_hash=make_password(otp),
        expires_at=expires_at
    )

    EmailOTP.objects.filter( expires_at__lte=timezone.now()).delete()

    try:
        send_mail(
            subject='RemindX Login OTP',
            message=f'Hello, Remindian. Your RemindX OTP is {otp}. It expires in 20 minutes.',
            from_email=None,  # use app email
            recipient_list=[email],  #user email
            fail_silently=False  #display error
        )

    except Exception as e:
        print("EMAIL ERROR:", repr(e))
        otp_record.delete()

        return JsonResponse({
            'success': False,
            'error': 'Unable to send OTP email'
        }, status=500)
    
    request.session["otp_email"] = email

    return JsonResponse({
        'success': True,
        'message': 'OTP sent successfully',
        'email' : email,
    })

@require_POST
def otp_verification(request):

    otp = request.POST.get("otp", "").strip()
    email = request.session.get("otp_email")
    
    if not email:
        return JsonResponse({
            "success": False,
            "message": "Email session not found"
        }, status=400)


    if len(otp) != 6:
        return JsonResponse({
            "success": False,
            "message": "Please enter a valid 6-digit OTP"
        }, status=400)

    verify = EmailOTP.objects.filter(email=email).order_by("-created_at").first()

    if verify is None:
        return JsonResponse({
            "success": False,
            "message": "OTP not found"
        }, status=400)

    if verify.expires_at <= timezone.now():
        verify.delete()

        return JsonResponse({
            "success": False,
            "message": "OTP has expired"
        }, status=400)


    if not check_password(otp, verify.otp_hash):
        return JsonResponse({
            "success": False,
            "message": "Incorrect OTP"
        }, status=400)


    User = get_user_model()

    user = User.objects.filter(email__iexact=email).first()

    if user is None:

        base_username = slugify(email.split("@")[0])[:120] or "Remindian"
        username = base_username

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{get_random_string(6)}"

        user = User.objects.create_user(
            username=username,
            email=email
        )   

    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    verify.delete()

    request.session.pop("otp_email", None)

    return JsonResponse({
        "success": True,
        "message": "OTP verified successfully"
    })

@require_POST
def reminder(request):
    title = request.POST.get("title")
    description = request.POST.get("description")
    date = request.POST.get("date")
    time = request.POST.get("time")

    Task.objects.create(
        title = title,
        description = description,
        date = date,
        time = time,
        user = request.user
    )

    return redirect('/')
