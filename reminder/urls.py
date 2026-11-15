from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('email_login/',views.email_login,name="emaillogin"),
]