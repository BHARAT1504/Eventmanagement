from django.urls import path
from . import views


urlpatterns = [
   path('register/', views.UserRegisterView.as_view(), name='user_list'),
   path('login/',views.UserLoginView.as_view(),name='login'),
   path('changepassword/',views.ChangePasswordView.as_view(),name='changepassword'),
  
   path('resetpassword/',views.SendPasswordResetEmailView.as_view(),name='resetpassword'),
   path('reset-password/<uid>/<token>/', views.UserPasswordResetView.as_view(), name='reset-password')
]