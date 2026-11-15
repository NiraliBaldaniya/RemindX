from django.contrib import admin
from django.urls import path,include
from reminder.views import home
from reminder.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reminder.urls')),
]
