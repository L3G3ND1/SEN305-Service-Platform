from django.core.management.base import BaseCommand
from django.db.models import Q
from requests_app.models import Category, ServiceRequest

class Command(BaseCommand):
    help = "Print SQL and EXPLAIN for open/assigned requests in Electrical ordered by priority/date."
    def handle(self, *args, **options):
        category = Category.objects.get(name="Electrical")
        queryset = ServiceRequest.objects.filter(category=category).filter(Q(status=ServiceRequest.Status.OPEN) | Q(status=ServiceRequest.Status.ASSIGNED)).order_by("priority", "created_at")
        self.stdout.write("Generated SQL:")
        self.stdout.write(str(queryset.query))
        self.stdout.write("EXPLAIN:")
        self.stdout.write(queryset.explain())
        self.stdout.write("Record the actual key/index shown by MySQL. If type=ALL / key=NULL, explain that the synthetic table is small and a table scan may be cheaper than index access.")
