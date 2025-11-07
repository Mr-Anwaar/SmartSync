from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetConfirmView

urlpatterns = [
    path("login", views.login, name='login'),
    path("register", views.register, name='register'),
    path("forgot_password", views.forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("logout", views.logout, name='logout'),
]
