from django.urls import path
from . import views

urlpatterns = [
    path("link-telegram/", views.link_telegram),
    path('today/<int:telegram_id>/', views.get_today_cards),
    path('progress/<int:telegram_id>/', views.get_progress),
]
