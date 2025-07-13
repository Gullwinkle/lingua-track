from django.urls import path
from tts import views

app_name = 'tts'

urlpatterns = [
    path('say/<str:word>/', views.say_word, name='say_word'),
    path('api/say/<str:word>/', views.say_word_api, name='say_word_api'),
    path('file/say/<str:word>/', views.say_word_file, name='say_word_file'),
]