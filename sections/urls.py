from django.urls import path
from . import views

app_name = 'sections'

urlpatterns = [
    path('', views.section_list, name='section_list'),
    path('create/', views.section_create, name='section_create'),
    path('<int:section_id>/', views.section_detail, name='section_detail'),
    path('<int:section_id>/edit/', views.section_update, name='section_update'),
    path('<int:section_id>/delete/', views.section_delete, name='section_delete'),
]