from .models import NurseTask

class NurseService:
    def assign_task(self, nurse, patient, task_type, description, due_date, priority=1):
        task = NurseTask.objects.create(
            nurse=nurse,
            patient=patient,
            task_type=task_type,
            description=description,
            due_date=due_date,
            priority=priority
        )
        return task
    
    def get_pending_tasks(self, nurse):
        return NurseTask.objects.filter(
            nurse=nurse,
            status__in=['pending', 'in_progress']
        )
