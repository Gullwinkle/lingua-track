from django.urls import path
from . import views

app_name = 'repetition'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('review/<int:schedule_id>/', views.review_card, name='review_card'),
    path('test/<int:schedule_id>/', views.test_multiple_choice, name='test_multiple_choice'),
]