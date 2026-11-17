from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from requests_app.models import Category, ServiceRequest

class Command(BaseCommand):
    help = "Create synthetic service requests for SEN305 ORM/query exercises."
    def handle(self, *args, **options):
        User = get_user_model()
        requester, _ = User.objects.get_or_create(username="lab_requester", defaults={"email": "lab_requester@example.test"})
        if not requester.has_usable_password():
            requester.set_password("LabOnly-ChangeMe123")
            requester.save()
        electrical, _ = Category.objects.get_or_create(name="Electrical", defaults={"description": "Synthetic electrical maintenance category"})
        plumbing, _ = Category.objects.get_or_create(name="Plumbing", defaults={"description": "Synthetic plumbing maintenance category"})
        statuses = [ServiceRequest.Status.OPEN, ServiceRequest.Status.ASSIGNED, ServiceRequest.Status.IN_PROGRESS]
        for i in range(12):
            category = electrical if i % 2 == 0 else plumbing
            status = statuses[i % len(statuses)]
            title = f"SYNTHETIC-{i+1:02d} {category.name} maintenance request"
            ServiceRequest.objects.get_or_create(title=title, requester=requester, defaults={
                "category": category, "description": "Synthetic laboratory data only.", "location": f"Lab Room {i+1}",
                "priority": (i % 5) + 1, "status": status,
                "due_at": timezone.now() + timedelta(days=(i - 4)),
            })
        self.stdout.write(self.style.SUCCESS("Created or confirmed 12 synthetic requests across two categories and three statuses."))
