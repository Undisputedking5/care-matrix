from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from .models import Patient, VitalSign, MedicalRecord, LabResult

# =====================================================
# PATIENT CRUD
# =====================================================
@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})

@login_required
def patient_create(request):
    if request.method == 'POST':
        patient = Patient.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            date_of_birth=request.POST.get('date_of_birth'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address')
        )
        return redirect('patients:patient_detail', pk=patient.id)
    return render(request, 'patients/create.html')

@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.gender = request.POST.get('gender')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.save()
        return redirect('patients:patient_detail', pk=patient.id)
    return render(request, 'patients/update.html', {'patient': patient})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/detail.html', {'patient': patient})

@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patients:patient_list')
    return render(request, 'patients/delete.html', {'patient': patient})

# =====================================================
# MEDICAL RECORDS
# =====================================================
@login_required
def add_record(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            MedicalRecord.objects.create(patient=patient, description=description)
            return redirect('patients:patient_detail', pk=patient.pk)
    return render(request, 'patients/add_record.html', {'patient': patient})

# =====================================================
# VITAL SIGNS
# =====================================================
@login_required
def add_vitals(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        VitalSign.objects.create(
            patient=patient,
            weight=float(request.POST.get('weight') or 0),
            height=float(request.POST.get('height') or 0),
            blood_pressure_systolic=int(request.POST.get('blood_pressure_systolic') or 0),
            blood_pressure_diastolic=int(request.POST.get('blood_pressure_diastolic') or 0),
            pulse=int(request.POST.get('pulse') or 0),
            temperature=float(request.POST.get('temperature') or 0),
            visit_date=date.today()
        )
        return redirect('patients:patient_detail', pk=patient.pk)
    return render(request, 'patients/add_vitals.html', {'patient': patient})

# =====================================================
# LAB RESULTS
# =====================================================
@login_required
def add_lab_result(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        LabResult.objects.create(
            patient=patient,
            test_name=request.POST.get('test_name'),
            result_value=request.POST.get('result_value'),
            status=request.POST.get('status'),
            notes=request.POST.get('notes'),
            test_date=request.POST.get('test_date') or date.today()
        )
        return redirect('patients:patient_detail', pk=patient.pk)
    return render(request, 'patients/add_lab.html', {'patient': patient})

@login_required
def dashboard_home(request):
    # -----------------------------
    # Total patients
    # -----------------------------
    patients_count = Patient.objects.count()

    # -----------------------------
    # Average BMI across all vitals
    # -----------------------------
    bmi_values = []
    for vital in VitalSign.objects.all():
        if vital.height > 0:
            bmi_values.append(vital.bmi)
    avg_bmi = round(sum(bmi_values)/len(bmi_values), 1) if bmi_values else 0

    # -----------------------------
    # High-risk patients
    # -----------------------------
    high_risk_patients = []
    for patient in Patient.objects.all():
        reasons = set()

        # Check latest vitals
        latest_vital = patient.vitals.order_by('-visit_date').first()
        if latest_vital:
            for reason in latest_vital.high_risk_reasons:
                reasons.add(reason)

        # Check labs
        abnormal_labs = patient.labs.filter(status='Abnormal')
        if abnormal_labs.exists():
            reasons.add("Abnormal Lab Result")

        if reasons:
            patient.high_risk_reasons = list(reasons)
            high_risk_patients.append(patient)

    context = {
        'patients_count': patients_count,
        'avg_bmi': avg_bmi,
        'high_risk_patients': high_risk_patients,
    }

    return render(request, 'dashboard/home.html', context)