from django.urls import path
from . import views

app_name = 'sections'

urlpatterns = [
    # Treasurer Section & Roster Management
    path('', views.section_list, name='section_list'),
    path('create/', views.section_create, name='section_create'),
    path('<int:section_id>/', views.section_detail, name='section_detail'),
    path('<int:section_id>/edit/', views.section_update, name='section_update'),
    path('<int:section_id>/delete/', views.section_delete, name='section_delete'),
    path('<int:section_id>/members/<int:membership_id>/toggle/', views.toggle_member_status, name='toggle_member_status'),
    path('<int:section_id>/members/<int:membership_id>/remove/', views.remove_member, name='remove_member'),

    # Member Onboarding & Section Views
    path('my/', views.member_section_list, name='member_section_list'),
    path('join/', views.join_section, name='join_section'),
    path('my/<int:section_id>/', views.member_section_detail, name='member_section_detail'),
]