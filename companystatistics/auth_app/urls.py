from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

import auth_app.views as auth_app
# from auth_app import views
from auth_app.views import UserLoginView, UserLogoutView, UserEditView, UserProfileView

app_name = 'auth_app'

urlpatterns = [
    # path('login/', auth_app.user_login, name='login'),
    path('login/', UserLoginView.as_view(), name='login'),
    # path('logout/', auth_app.user_logout, name='logout'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # path('edit/', auth_app.user_edit, name='edit'),
    path('edit/', UserEditView.as_view(), name='edit'),
    # path('profile/', auth_app.user_profile, name='profile'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # change password urls
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             success_url=reverse_lazy('auth_app:password_change_done')
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    # reset password urls
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             success_url=reverse_lazy('auth_app:password_reset_done')
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]