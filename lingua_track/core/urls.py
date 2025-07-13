from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('card/create/', views.card_create, name='card_create'),
    path('card/<int:card_id>/edit/', views.card_edit, name='card_edit'),
    path('card/<int:card_id>/delete/', views.card_delete, name='card_delete'),
    path('progress/', views.progress, name='progress'),
    path('telegram-link/', views.telegram_link, name='telegram_link'),
]