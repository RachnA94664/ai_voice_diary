from django.urls import path
from . import views
from . import api
from .views import text_entry_upload, voice_entry_upload

app_name = 'diary'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('record/', views.create_diary_entry, name='record_entry'),
    
    # Entry CRUD operations
    path('create/', views.create_diary_entry, name='create_entry'),
    path('entries/', views.entry_list, name='entry_list'),
    path('entries/<int:pk>/', views.entry_detail, name='entry_detail'),
    path('entries/<int:pk>/edit/', views.entry_update, name='entry_update'),
    path('entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    
    # API endpoints
    path('api/entries/', api.entry_list_api, name='entry_list_api'),
    path('api/entries/<int:pk>/', api.entry_delete_api, name='entry_delete_api'),
    path('api/entries/text/', text_entry_upload, name='text_entry_upload'),
    path('api/entries/voice/', voice_entry_upload, name='voice_entry_upload'),
]
