from django.contrib import admin
from .models import Patient, VitalSign, MedicalRecord, LabResult

admin.site.register(Patient)
admin.site.register(VitalSign)
admin.site.register(MedicalRecord)
admin.site.register(LabResult)
