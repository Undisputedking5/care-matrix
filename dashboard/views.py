from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from patients.models import Patient, VitalSign, MedicalRecord, LabResult

@login_required
def dashboard_home(request):
    # Total patients
    patients_count = Patient.objects.count()

    # Average BMI across all vitals
    vitals = VitalSign.objects.all()
    bmi_values = [v.bmi for v in vitals if v.height > 0]
    avg_bmi = round(sum(bmi_values)/len(bmi_values), 1) if bmi_values else 0

    # High-risk patients
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

    # Recent Vitals and Labs
    recent_vitals = VitalSign.objects.order_by('-visit_date', '-id')[:5]
    recent_labs = LabResult.objects.order_by('-test_date', '-id')[:5]

    # Bed Occupancy Metrics
    from patients.models import Bed
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    available_beds = total_beds - occupied_beds
    occupancy_rate = round((occupied_beds / total_beds * 100) if total_beds > 0 else 0)

    context = {
        'patients_count': patients_count,
        'avg_bmi': avg_bmi,
        'high_risk_patients': high_risk_patients,
        'recent_vitals': recent_vitals,
        'recent_labs': recent_labs,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_rate': occupancy_rate,
    }

    return render(request, 'dashboard/home.html', context)