from django.urls import path
from .views import register,login_view, logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
]