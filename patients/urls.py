from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patient CRUD
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update, name='patient_update'),
    path('<int:pk>/add_record/', views.add_record, name='add_record'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('<int:pk>/add_vitals/', views.add_vitals, name='add_vitals'),
    path('<int:pk>/add_lab/', views.add_lab_result, name='add_lab'),
    
    # Ward & Bed Management
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/<int:pk>/', views.ward_detail, name='ward_detail'),
    path('<int:pk>/admit/', views.admit_patient, name='admit_patient'),
    path('<int:pk>/discharge/', views.discharge_patient, name='discharge_patient'),
]