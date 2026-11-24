from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('email_login/',views.email_login,name="emaillogin"),
    path('otp_verification/',views.otp_verification,name="otp_verification"),
    path('home/',views.home,name="home page"),
    path('logout/', views.user_logout, name='logout'),
    path('reminder/', views.reminder, name='reminder'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
]