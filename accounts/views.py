from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    """Handle login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard:dashboard_home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')


def signup_view(request):
    """Handle signup page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('accounts:login')
    return render(request, 'accounts/signup.html')


def logout_view(request):
    """Logs out the user"""
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')
    return render(request, 'accounts/logout.html')