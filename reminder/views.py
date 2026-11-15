from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import EmailOTP
from secrets import randbelow
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

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

    otp = str(randbelow(900000)+ (100000))
    
    expires_at = timezone.now() + timedelta(minutes=5)

    EmailOTP.objects.create(
        email=email,
        otp_hash = make_password(otp),
        expires_at = expires_at
    )

    return JsonResponse({
        'success': True
        })

