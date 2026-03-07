from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from patients.models import Patient, VitalSign, LabResult, MedicalRecord, Ward, Bed

import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =====================================================
# PATIENT LIST
# =====================================================

@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})


# =====================================================
# CREATE PATIENT
# =====================================================

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


# =====================================================
# UPDATE PATIENT
# =====================================================

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


# =====================================================
# PATIENT DETAIL + GRAPH
# =====================================================

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    vitals = patient.vitals.order_by('-visit_date')[:20]
    vitals = list(reversed(vitals))

    labels = [v.visit_date.strftime("%d/%m") for v in vitals]
    systolic = [v.blood_pressure_systolic for v in vitals]
    diastolic = [v.blood_pressure_diastolic for v in vitals]

    graph = None

    if vitals:
        plt.figure(figsize=(8, 4))
        plt.plot(labels, systolic, marker='o')
        plt.plot(labels, diastolic, marker='o')
        plt.title(f"{patient.first_name} {patient.last_name} - Blood Pressure")
        plt.xlabel("Date")
        plt.ylabel("Blood Pressure")
        plt.legend(["Systolic", "Diastolic"])
        plt.xticks(rotation=45)

        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        graph = base64.b64encode(image_png).decode('utf-8')

    context = {
        'patient': patient,
        'graph': graph
    }

    return render(request, 'patients/detail.html', context)


# =====================================================
# ADD VITALS
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
# ADD LAB RESULT
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


# =====================================================
# ADD MEDICAL RECORD
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
# DELETE PATIENT
# =====================================================

@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.delete()
        return redirect('patients:patient_list')

    return render(request, 'patients/delete.html', {'patient': patient})


# =====================================================
# WARD MANAGEMENT
# =====================================================

@login_required
def ward_list(request):
    wards = Ward.objects.all()
    # Add occupancy stats to wards
    for ward in wards:
        ward.occupied_count = ward.beds.filter(is_occupied=True).count()
        ward.total_beds = ward.beds.count()
    return render(request, 'patients/ward_list.html', {'wards': wards})

@login_required
def ward_detail(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    beds = ward.beds.all().select_related('occupant')
    return render(request, 'patients/ward_detail.html', {'ward': ward, 'beds': beds})

@login_required
def admit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    # If explicitly discharging and trying to re-admit without bed check
    if patient.current_bed:
        # Already admitted
        return redirect('patients:patient_detail', pk=patient.pk)
        
    available_beds = Bed.objects.filter(is_occupied=False)
    
    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        if bed_id:
            bed = get_object_or_404(Bed, id=bed_id)
            patient.current_bed = bed
            patient.save()
            bed.is_occupied = True
            bed.save()
            return redirect('patients:patient_detail', pk=patient.pk)

    return render(request, 'patients/admit_patient.html', {
        'patient': patient, 
        'available_beds': available_beds
    })

@login_required
def discharge_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST' and patient.current_bed:
        bed = patient.current_bed
        bed.is_occupied = False
        bed.save()
        
        patient.current_bed = None
        patient.save()
        return redirect('patients:patient_detail', pk=patient.pk)
        
    return redirect('patients:patient_detail', pk=patient.pk)