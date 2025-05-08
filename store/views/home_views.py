# store/views/home_views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

def home_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'staff':
            return redirect('store:staff_dashboard')
        elif request.user.role == 'customer':
            return redirect('store:shop_home')
        else:
            # Fallback for users with no role or unexpected role
            return render(request, 'store/home.html', {'message': 'Welcome! Your role is not configured for a dashboard.'})
    return render(request, 'store/home.html')
