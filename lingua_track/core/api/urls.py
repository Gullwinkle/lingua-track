from django.urls import path
from core.api import views

app_name = 'api'

urlpatterns = [
    path('today/', views.today_words, name='today_words'),
    path('cards/', views.user_cards, name='user_cards'),
    path('progress/', views.progress, name='progress'),
    path('say/<str:word>/', views.say_word, name='say_word'),
    path('test/', views.test_card, name='test_card'),
    path('test/submit/', views.submit_test_answer, name='submit_test_answer'),
]