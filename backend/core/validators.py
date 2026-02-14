from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

def validate_file_size(file):
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(f"File size cannot exceed 10MB. Current size: {file.size / (1024*1024):.2f}MB")

def validate_medical_document(file):
    validate_file_size(file)
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
    validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
    validator(file)
    
def validate_image_file(file):
    validate_file_size(file)
    allowed_extensions = ['jpg', 'jpeg', 'png']
    validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
    validator(file)

def validate_blood_pressure(systolic, diastolic):
    if systolic < 70 or systolic > 250:
        raise ValidationError("Invalid systolic blood pressure")
    if diastolic < 40 or diastolic > 150:
        raise ValidationError("Invalid diastolic blood pressure")
    if systolic <= diastolic:
        raise ValidationError("Systolic must be greater than diastolic")

def validate_heart_rate(heart_rate):
    if heart_rate < 30 or heart_rate > 250:
        raise ValidationError("Invalid heart rate")

def validate_temperature(temperature):
    if temperature < 95.0 or temperature > 107.0:
        raise ValidationError("Invalid temperature")

def validate_spo2(spo2):
    if spo2 < 50 or spo2 > 100:
        raise ValidationError("Invalid SpO2 level")
