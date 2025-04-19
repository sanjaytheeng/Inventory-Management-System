from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User, UserActivity
from django.contrib.auth.views import LoginView

# Create your views here.

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        UserActivity.objects.create(
            user=self.object,
            action='registration',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        UserActivity.objects.create(
            user=form.get_user(),
            action='login',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return response

@login_required
def user_logout(request):
    UserActivity.objects.create(
        user=request.user,
        action='logout',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('authentication:login')

@method_decorator(login_required, name='dispatch')
class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'authentication/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        UserActivity.objects.create(
            user=self.object,
            action='profile_update',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        messages.success(self.request, 'Profile updated successfully!')
        return response

@login_required
def user_activity(request):
    activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'authentication/activity.html', {'activities': activities})
