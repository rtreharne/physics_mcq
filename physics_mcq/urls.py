"""
URL configuration for physics_mcq project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls import handler404

handler404 = 'mcq.views.custom_404'


from urllib.parse import urlencode

def redirect_to_google_login(request):
    next_url = request.GET.get('next', '/')
    google_login_url = '/accounts/google/login/?' + urlencode({'next': next_url})
    return redirect(google_login_url)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', redirect_to_google_login, name='account_login'),
    path('accounts/', include('allauth.urls')),
    path('', include('mcq.urls')),
]
