from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html'), name='logout'),
    path('login/', LoginView.as_view(template_name='users/login.html',
                                     extra_context={'card_title': 'Войти на сайт', 'button_text': 'Подтвердить'}),
         name='login'),
    path('signup/',
         views.SignUp.as_view(extra_context={'card_title': 'Зарегистрироваться', 'button_text': 'Подтвердить'}),
         name='signup'),
    path('password_reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html'),
         name='password_reset'),

    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='reset_done'),
    path('password_change/',
         PasswordChangeView.as_view(template_name='users/password_change_form.html', success_url='done'),
         name='password_change'),
    path('password_change/done', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
]
