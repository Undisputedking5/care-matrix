from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('register-doctor/', views.doctor_register, name='doctor_register'),
    path('', views.login_view, name='root'),
    path('doctor/delete/<int:id>/', views.doctor_delete, name='doctor_delete'),
    path('performance/', views.doctor_performance, name='doctor_performance'),
    path('audit-log/', views.audit_log, name='audit_log'),

]