from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('cards/', include('cards.urls')), # основной интерфейс — карточки
    path('api/', include('api.urls')),
]
