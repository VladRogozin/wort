from django.contrib import admin
from django.urls import path

from django.urls import path, include

urlpatterns = [
    path('', include('playlist.urls')),
    path('games/', include('games.urls')),
    path('accounts/', include('accounts.urls')),
    path('results/', include('results.urls')),
    path('admin/', admin.site.urls),
]