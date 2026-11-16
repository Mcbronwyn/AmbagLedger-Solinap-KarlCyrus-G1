from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def setup_check(request):
    return render(request, 'base.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', setup_check, name='home'),
]