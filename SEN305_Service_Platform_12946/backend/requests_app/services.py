from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Comment, ServiceRequest, WorkOrder

def service_request_create(*, requester, category, title, description, location, priority):
    item = ServiceRequest(requester=requester, category=category, title=title, description=description, location=location, priority=priority)
    item.full_clean()
    item.save()
    return item

def service_request_update(*, item, actor, category, title, description, location, priority):
    if not actor.is_staff and item.requester_id != actor.pk:
        raise ValidationError("You cannot update this request.")
    if item.status in (ServiceRequest.Status.RESOLVED, ServiceRequest.Status.CLOSED):
        raise ValidationError("Resolved requests cannot be edited.")
    item.category, item.title, item.description, item.location, item.priority = category, title, description, location, priority
    item.full_clean()
    item.save()
    return item

def comment_create(*, item, author, body):
    return Comment.objects.create(service_request=item, author=author, body=body)

@transaction.atomic
def service_request_assign(*, item_id, technician, actor):
    if not actor.is_staff:
        raise ValidationError("Only staff can assign requests.")
    item = ServiceRequest.objects.select_for_update().get(pk=item_id)
    if item.status in (ServiceRequest.Status.RESOLVED, ServiceRequest.Status.CLOSED):
        raise ValidationError("A completed request cannot be assigned.")
    order, _ = WorkOrder.objects.get_or_create(service_request=item, defaults={"technician": technician, "started_at": timezone.now()})
    if order.technician_id != technician.pk:
        order.technician = technician
        order.save(update_fields=["technician"])
    item.status = ServiceRequest.Status.ASSIGNED
    item.full_clean()
    item.save(update_fields=["status", "updated_at"])
    return item, order

@transaction.atomic
def service_request_resolve(*, item_id, actor, work_notes, resolution_summary):
    item = ServiceRequest.objects.select_for_update().select_related("work_order").get(pk=item_id)
    if not actor.is_staff and (not hasattr(item, "work_order") or item.work_order.technician_id != actor.pk):
        raise ValidationError("Only staff or the assigned technician can resolve this request.")
    if not hasattr(item, "work_order"):
        raise ValidationError("The request must be assigned before it can be resolved.")
    now = timezone.now()
    item.status = ServiceRequest.Status.RESOLVED
    item.resolved_at = now
    item.resolution_summary = resolution_summary.strip()
    item.full_clean()
    item.save(update_fields=["status", "resolved_at", "resolution_summary", "updated_at"])
    order = item.work_order
    order.work_notes = work_notes
    order.completed_at = now
    order.save(update_fields=["work_notes", "completed_at"])
    return item
