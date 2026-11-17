# Lab 4 transaction rollback evidence

Use only synthetic records. Open `python manage.py shell` and run:

```python
from django.contrib.auth import get_user_model
from django.db import transaction
from requests_app.models import ServiceRequest, WorkOrder

User = get_user_model()
item = ServiceRequest.objects.filter(status="open", title__startswith="SYNTHETIC-").first()
tech = User.objects.get(username="lab_requester")
before_status = item.status
before_count = WorkOrder.objects.filter(service_request=item).count()
try:
    with transaction.atomic():
        WorkOrder.objects.create(service_request=item, technician=tech)
        item.status = "assigned"
        item.save(update_fields=["status", "updated_at"])
        raise RuntimeError("Deliberate rollback demonstration")
except RuntimeError as exc:
    print(exc)
item.refresh_from_db()
after_count = WorkOrder.objects.filter(service_request=item).count()
print("Status:", before_status, "->", item.status)
print("Work orders:", before_count, "->", after_count)
```

Expected: status and work-order count are unchanged because the deliberate exception rolls back the transaction. This is a manual demonstration; run it on the configured local database and capture the actual terminal output.
