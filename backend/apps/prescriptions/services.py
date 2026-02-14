from .models import Prescription, PrescriptionMedicine

class PrescriptionService:
    def create_prescription(self, patient, doctor, diagnosis, medicines_data):
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            diagnosis=diagnosis
        )
        
        for medicine_data in medicines_data:
            PrescriptionMedicine.objects.create(
                prescription=prescription,
                **medicine_data
            )
        
        return prescription
