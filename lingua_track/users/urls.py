# project-level urls.py или users/urls.py
from django.urls import path
from users import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),  # теперь это пустой путь
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
