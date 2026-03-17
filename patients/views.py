from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from datetime import date
from patients.models import Patient, VitalSign, LabResult, MedicalRecord, Ward, Bed, HandoverNote, Appointment, AuditLog
from accounts.models import DoctorProfile

def is_admin(user):
    return user.is_superuser

import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


@login_required
def patient_list(request):
    query = request.GET.get('q')
    if query:
        patients = Patient.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients, 'query': query})



@login_required
def patient_create(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    if request.method == 'POST':
        patient = Patient.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            date_of_birth=request.POST.get('date_of_birth'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            doctor=request.POST.get('doctor')
        )
        actor = request.user.get_full_name() or request.user.username
        AuditLog.objects.create(
            user=actor,
            action='CREATE',
            description=f"New patient registered: {patient.first_name} {patient.last_name}"
        )
        return redirect('patients:patient_detail', pk=patient.id)

    return render(request, 'patients/create.html', {'doctors': doctors})


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
        patient.doctor = request.POST.get('doctor')
        patient.save()
        AuditLog.objects.create(
            user=request.user.get_full_name() or request.user.username,
            action='UPDATE',
            description=f"Patient details updated: {patient.first_name} {patient.last_name}"
        )
        return redirect('patients:patient_detail', pk=patient.id)

    return render(request, 'patients/update.html', {'patient': patient})


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
        # Define chart line colors fitting the theme
        plt.plot(labels, systolic, marker='o', color='#0dcaf0', label='Systolic')
        plt.plot(labels, diastolic, marker='o', color='#dc3545', label='Diastolic')
        
        plt.title(f"{patient.first_name} {patient.last_name} - Blood Pressure", color='white')
        plt.xlabel("Date", color='white')
        plt.ylabel("Blood Pressure", color='white')
        
        # Legend with transparent background & white text
        legend = plt.legend()
        plt.setp(legend.get_texts(), color='white')
        if legend.get_frame():
            legend.get_frame().set_facecolor('none')
            legend.get_frame().set_edgecolor((1, 1, 1, 0.2))
        
        # Ticks and Axis Spines
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        
        ax = plt.gca()
        ax.set_facecolor('none')
        for spine in ax.spines.values():
            spine.set_color((1, 1, 1, 0.2))

        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', transparent=True)
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
def add_record(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            MedicalRecord.objects.create(patient=patient, description=description)
            return redirect('patients:patient_detail', pk=patient.pk)

    return render(request, 'patients/add_record.html', {'patient': patient})






@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        p_name = f"{patient.first_name} {patient.last_name}"
        patient.delete()
        AuditLog.objects.create(
            user=request.user.get_full_name() or request.user.username,
            action='DELETE',
            description=f"Patient deleted: {p_name}"
        )
        return redirect('patients:patient_list')

    return render(request, 'patients/delete.html', {'patient': patient})



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
            AuditLog.objects.create(
                user=request.user.get_full_name() or request.user.username,
                action='ADMIT',
                description=f"Patient {patient.first_name} {patient.last_name} admitted to {bed.ward.name} Bed {bed.bed_number}"
            )
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
        AuditLog.objects.create(
            user=request.user.get_full_name() or request.user.username,
            action='DISCHARGE',
            description=f"Patient {patient.first_name} {patient.last_name} discharged from {bed.ward.name} Bed {bed.bed_number}"
        )
        return redirect('patients:patient_detail', pk=patient.pk)
        
    return redirect('patients:patient_detail', pk=patient.pk)


@login_required
@user_passes_test(is_admin)
def ward_create(request):
    if request.method == 'POST':
        ward = Ward.objects.create(
            name=request.POST.get('name'),
            ward_type=request.POST.get('ward_type'),
            capacity=int(request.POST.get('capacity') or 0)
        )
        return redirect('patients:ward_detail', pk=ward.id)

    return render(request, 'patients/ward_create.html', {
        'ward_types': Ward.WARD_TYPES
    })


@login_required
@user_passes_test(is_admin)
def ward_update(request, pk):
    ward = get_object_or_404(Ward, pk=pk)

    if request.method == 'POST':
        ward.name = request.POST.get('name')
        ward.ward_type = request.POST.get('ward_type')
        ward.capacity = int(request.POST.get('capacity') or 0)
        ward.save()
        return redirect('patients:ward_detail', pk=ward.id)

    return render(request, 'patients/ward_update.html', {
        'ward': ward,
        'ward_types': Ward.WARD_TYPES
    })



@login_required
@user_passes_test(is_admin)
def ward_delete(request, pk):
    ward = get_object_or_404(Ward, pk=pk)

    if request.method == 'POST':
        ward.delete()
        return redirect('patients:ward_list')

    return render(request, 'patients/ward_delete.html', {'ward': ward})



@login_required
@user_passes_test(is_admin)
def bed_create(request, ward_id):
    ward = get_object_or_404(Ward, id=ward_id)

    if request.method == 'POST':
        Bed.objects.create(
            ward=ward,
            bed_number=request.POST.get('bed_number')
        )
        return redirect('patients:ward_detail', pk=ward.id)

    return render(request, 'patients/bed_create.html', {'ward': ward})



@login_required
@user_passes_test(is_admin)
def bed_update(request, pk):
    bed = get_object_or_404(Bed, pk=pk)

    if request.method == 'POST':
        bed.bed_number = request.POST.get('bed_number')
        bed.save()
        return redirect('patients:ward_detail', pk=bed.ward.id)

    return render(request, 'patients/bed_update.html', {'bed': bed})



@login_required
@user_passes_test(is_admin)
def bed_delete(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    ward_id = bed.ward.id

    if request.method == 'POST':
        bed.delete()
        return redirect('patients:ward_detail', pk=ward_id)

    return render(request, 'patients/bed_delete.html', {'bed': bed})



# -----------------------------------------------
# Handover Notes
# -----------------------------------------------
@login_required
def add_handover_note(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        note_text = request.POST.get('note')
        if note_text:
            written_by = request.user.get_full_name() or request.user.username
            HandoverNote.objects.create(patient=patient, written_by=written_by, note=note_text)
            AuditLog.objects.create(
                user=written_by,
                action='NOTE',
                description=f"Handover note written for patient: {patient.first_name} {patient.last_name}"
            )
            return redirect('patients:patient_detail', pk=patient.pk)
    return redirect('patients:patient_detail', pk=patient.pk)


# -----------------------------------------------
# Appointments
# -----------------------------------------------
@login_required
def book_appointment(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        doctor = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        if appointment_date and appointment_time and reason:
            appt = Appointment.objects.create(
                patient=patient,
                doctor=doctor or request.user.get_full_name() or request.user.username,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason
            )
            AuditLog.objects.create(
                user=request.user.get_full_name() or request.user.username,
                action='APPOINTMENT',
                description=f"Appointment booked for {patient.first_name} {patient.last_name} on {appointment_date} at {appointment_time}"
            )
            return redirect('patients:patient_detail', pk=patient.pk)
    return render(request, 'patients/book_appointment.html', {'patient': patient})


@login_required
def appointment_list(request):
    today = date.today()
    upcoming = Appointment.objects.filter(appointment_date__gte=today, is_completed=False).select_related('patient')
    past = Appointment.objects.filter(appointment_date__lt=today).select_related('patient')[:20]
    return render(request, 'patients/appointment_list.html', {
        'upcoming': upcoming,
        'past': past,
        'today': today,
    })


@login_required
def complete_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    appt.is_completed = True
    appt.save()
    return redirect('patients:appointment_list')
