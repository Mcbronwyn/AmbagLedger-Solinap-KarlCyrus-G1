from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
    path('dashboard/treasurer/', views.treasurer_dashboard_view, name='treasurer_dashboard'),
    path('dashboard/member/', views.member_dashboard_view, name='member_dashboard'),
]