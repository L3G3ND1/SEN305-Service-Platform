from django.db.models import Count, Q
from .models import ServiceRequest

def visible_requests(user):
    qs = ServiceRequest.objects.select_related("category", "requester").annotate(comment_count=Count("comments", distinct=True))
    if user.is_staff:
        return qs
    return qs.filter(requester=user)

def request_detail_for_user(user, request_id):
    return visible_requests(user).prefetch_related("comments__author", "work_order").get(pk=request_id)

def request_summary_counts(user):
    qs = ServiceRequest.objects.all()
    if not user.is_staff:
        qs = qs.filter(requester=user)
    values = qs.aggregate(
        open_count=Count("id", filter=Q(status=ServiceRequest.Status.OPEN)),
        assigned_count=Count("id", filter=Q(status=ServiceRequest.Status.ASSIGNED)),
        resolved_count=Count("id", filter=Q(status=ServiceRequest.Status.RESOLVED)),
    )
    return values
