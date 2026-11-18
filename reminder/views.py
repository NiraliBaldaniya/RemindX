from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import EmailOTP
from secrets import randbelow
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password,check_password
from django.core.mail import send_mail

def home(request):
    return render(request,'index.html')

def login(request):
    return render(request,'registration/login.html')


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

    try:
        send_mail(
            subject='RemindX Login OTP',
            message=f'Your RemindX OTP is {otp}. It expires in 20 minutes.',
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
        'message': 'OTP sent successfully'
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

    verify.delete()

    request.session["verified_email"] = email
    request.session.pop("otp_email", None)

    return JsonResponse({
        "success": True,
        "message": "OTP verified successfully"
    })