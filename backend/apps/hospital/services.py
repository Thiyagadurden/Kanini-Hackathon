from .models import HospitalResource

class HospitalService:
    def update_resource_availability(self, resource_id, change_amount):
        resource = HospitalResource.objects.get(id=resource_id)
        resource.available_quantity += change_amount
        if resource.available_quantity < 0:
            resource.available_quantity = 0
        if resource.available_quantity > resource.total_quantity:
            resource.available_quantity = resource.total_quantity
        resource.save()
        return resource
