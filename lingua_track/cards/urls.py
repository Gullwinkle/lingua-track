from django.urls import path
from . import views

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('add/', views.card_add, name='card_add'),
    path('<int:card_id>/', views.card_detail, name='card_detail'),  # Для просмотра
    path('<int:card_id>/edit/', views.card_edit, name='card_edit'),  # Для редактирования
    path('<int:card_id>/delete/', views.card_delete, name='card_delete'),  # Для удаления
    path('review/', views.review_today, name='review_today'),
    path('review/<int:schedule_id>/<int:quality>/', views.review_result, name='review_result'),
    path("cards/test/", views.card_test, name="card_test"),
]
