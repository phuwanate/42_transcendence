from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("user_register", views.user_register),
    path("auth/login", views.UserLogin, name="userLogin"),
    path("auth/register", views.UserRegister, name="userRegister"),
    path("auth/logout", views.UserLogout, name="userLogout"),
    path("get_csrf_token_and_session_id/", views.get_csrf_token_and_session_id, name="csrft_session"),
]