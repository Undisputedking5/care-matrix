from django.contrib import admin
from .models import Patient, VitalSign, MedicalRecord, LabResult, Ward, Bed

admin.site.register(Patient)
admin.site.register(VitalSign)
admin.site.register(MedicalRecord)
admin.site.register(LabResult)
admin.site.register(Ward)
admin.site.register(Bed)
