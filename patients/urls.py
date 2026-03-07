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
]