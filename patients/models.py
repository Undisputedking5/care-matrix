from django.db import models
from datetime import date

# Existing Patient model
class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    is_high_risk = models.BooleanField(default=False)

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