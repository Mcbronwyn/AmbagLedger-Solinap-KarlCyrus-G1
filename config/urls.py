from django.contrib import admin
from django.urls import include, path
from accounts.views import dashboard_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_redirect_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('sections/', include('sections.urls')),
]