from django.urls import path
from core.api import views
from tts import views as tts_views

app_name = 'api'

urlpatterns = [
    path('today/', views.today, name='today'),
    path('cards/', views.cards, name='cards'),
    path('progress/', views.progress, name='progress'),
    path('file/say/<str:word>/', tts_views.say_word_file, name='say_word'),
    path('test/', views.test, name='test'),
    path('test/submit/', views.test_submit, name='test_submit'),
]