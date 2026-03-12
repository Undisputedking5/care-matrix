from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import DoctorProfile


def admin_check(user):
    return user.is_superuser


def login_view(request):
    """Handle login page with dual mode (Admin/Doctor)"""
    if request.method == 'POST':
        login_type = request.POST.get('login_type')  # 'admin' or 'doctor'
        username = request.POST.get('username')
        password = request.POST.get('password')

        if login_type == 'doctor':
            # For doctor, password field contains the doctor_id
            try:
                doctor_profile = DoctorProfile.objects.get(doctor_id=password)
                # Authenticate matching user with that same doctor_id
                user = authenticate(request, username=doctor_profile.user.username, password=password)
            except DoctorProfile.DoesNotExist:
                user = None
        else:
            # Traditional admin login
            user = authenticate(request, username=username, password=password)

        if user:
            if login_type == 'admin' and not user.is_superuser:
                messages.error(request, "Access denied. Only superusers can log in via Admin mode.")
            else:
                login(request, user)
                if user.is_superuser:
                    return redirect('accounts:admin_dashboard')
                return redirect('dashboard:dashboard_home')
        else:
            if login_type == 'doctor':
                messages.error(request, "Invalid Doctor ID.")
            else:
                messages.error(request, "Invalid username or password.")
                
    return render(request, 'accounts/login.html')


@login_required
@user_passes_test(admin_check)
def admin_dashboard(request):
    """Admin dashboard to manage doctors"""
    doctors = DoctorProfile.objects.all().select_related('user')
    return render(request, 'accounts/admin_dashboard.html', {'doctors': doctors})


@login_required
@user_passes_test(admin_check)
def doctor_register(request):
    """Register a new doctor"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        doctor_id = request.POST.get('doctor_id')
        department = request.POST.get('department')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif DoctorProfile.objects.filter(doctor_id=doctor_id).exists():
            messages.error(request, "Doctor ID already exists.")
        else:
            # Create user with doctor_id as password
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=doctor_id,
                first_name=first_name,
                last_name=last_name
            )
            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                doctor_id=doctor_id,
                department=department,
                phone=phone
            )
            messages.success(request, f"Doctor {first_name} {last_name} registered successfully!")
            return redirect('accounts:admin_dashboard')

    return render(request, 'accounts/doctor_register.html')


def signup_view(request):
    """Signup is now restricted. Only Admin can register users."""
    messages.warning(request, "Public signup is disabled. Please contact the Admin.")
    return redirect('accounts:login')


def logout_view(request):
    """Logs out the user"""
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')
    # If GET, redirect to login
    return redirect('accounts:login')



def doctor_delete(request, id):
    doctor = get_object_or_404(DoctorProfile, id=id)

    if request.method == "POST":
        doctor.user.delete()
        # return redirect('admin_dashboard')

    return redirect('accounts:admin_dashboard')