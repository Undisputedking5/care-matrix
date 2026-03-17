from django.db import models
from datetime import date

# -----------------------------
# Ward & Bed Models
# -----------------------------
class Ward(models.Model):
    WARD_TYPES = (
        ('General', 'General'),
        ('ICU', 'ICU'),
        ('Maternity', 'Maternity'),
        ('Pediatric', 'Pediatric'),
    )
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES, default='General')
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.ward_type})"

class Bed(models.Model):
    ward = models.ForeignKey(Ward, related_name='beds', on_delete=models.CASCADE)
    bed_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"{self.ward.name} - Bed {self.bed_number} ({status})"

# -----------------------------
# Existing Patient model
# -----------------------------
class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    doctor = models.CharField(blank=True, null=True, max_length=100)
    is_high_risk = models.BooleanField(default=False)

    # Optional assignment to a bed
    current_bed = models.OneToOneField(Bed, null=True, blank=True, on_delete=models.SET_NULL, related_name='occupant')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# VitalSign model
class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, related_name='vitals', on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    pulse = models.IntegerField()
    temperature = models.FloatField()
    visit_date = models.DateField(default=date.today)

    @property
    def bmi(self):
        if self.height > 0:
            return round(self.weight / (self.height ** 2), 1)
        return 0

    @property
    def high_risk_reasons(self):
        reasons = []
        if self.blood_pressure_systolic >= 140 or self.blood_pressure_diastolic >= 90:
            reasons.append("High Blood Pressure")
        if self.bmi >= 25:
            reasons.append("High BMI")
        if self.pulse >= 120:
            reasons.append("High Pulse")
        if self.temperature >= 38:
            reasons.append("High Temperature")
        return reasons

# -----------------------------
# MedicalRecord model (must exist!)
# -----------------------------
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, related_name='records', on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# LabResult model
class LabResult(models.Model):
    STATUS_CHOICES = (
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
    )
    patient = models.ForeignKey(Patient, related_name='labs', on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    result_value = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    test_date = models.DateField(default=date.today)


# -----------------------------
# Handover Notes
# -----------------------------
class HandoverNote(models.Model):
    patient = models.ForeignKey(Patient, related_name='handover_notes', on_delete=models.CASCADE)
    written_by = models.CharField(max_length=150)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Handover by {self.written_by} for {self.patient} on {self.created_at.date()}"


# -----------------------------
# Appointments
# -----------------------------
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.CharField(max_length=150)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=250)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    def __str__(self):
        return f"{self.patient} - {self.appointment_date} {self.appointment_time}"


# -----------------------------
# Audit Log
# -----------------------------
class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('ADMIT', 'Admit'),
        ('DISCHARGE', 'Discharge'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('NOTE', 'Handover Note'),
        ('APPOINTMENT', 'Appointment'),
    )
    user = models.CharField(max_length=150)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.action}] {self.user} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"