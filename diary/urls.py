from django.urls import path
from . import views

# app_name = 'diary'  # This registers the namespace for the app

urlpatterns = [
    path('', views.home, name='home'),           # Root URL redirects appropriately
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('entries/', views.entry_list, name='entry_list'), 
]
