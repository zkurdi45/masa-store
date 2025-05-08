from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
# HttpResponse is no longer needed here as home_view is moved
from store.forms import CustomUserCreationForm # CustomAuthenticationForm removed

# home_view was here, now moved to home_views.py

class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'store/register.html'
    success_url = reverse_lazy('store:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class UserLoginView(LoginView):
    # form_class = CustomAuthenticationForm # Removed this line, LoginView uses default AuthenticationForm
    template_name = 'store/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if getattr(user, 'role', None) == 'staff':
                # return reverse_lazy('store:staff_dashboard')
                pass
            elif getattr(user, 'role', None) == 'customer':
                # return reverse_lazy('store:customer_dashboard')
                pass
        return reverse_lazy('store:home')

class UserLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('store:login')
