from django.contrib import admin
from django.urls import path, include
from diary.views import home

urlpatterns = [
    path('', home, name='home'),  # New: root url
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('diary/', include('diary.urls')),

    # Add other app urls like 'diary/' or 'expenses/' here later
]
