from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('activity/', views.user_activity, name='activity'),
] 