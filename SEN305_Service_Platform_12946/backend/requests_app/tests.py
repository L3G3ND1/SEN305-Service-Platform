from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Category, ServiceRequest, WorkOrder
from .services import service_request_assign, service_request_resolve
User = get_user_model()

class ServiceRequestModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="requester", password="pass12345")
        self.category = Category.objects.create(name="Facilities")
    def make_request(self, **kwargs):
        data = dict(requester=self.user, category=self.category, title="Broken laboratory socket", description="Socket has no power.", location="Block A", priority=2)
        data.update(kwargs)
        return ServiceRequest.objects.create(**data)
    def test_uuid_primary_key(self):
        item = self.make_request()
        self.assertIsNotNone(item.id)
    def test_category_name_is_unique(self):
        duplicate = Category(name="Facilities")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
    def test_priority_outside_range_fails_full_clean(self):
        item = ServiceRequest(requester=self.user, category=self.category, title="Bad priority", description="Test", location="Lab", priority=7)
        with self.assertRaises(ValidationError):
            item.full_clean()
    def test_resolved_requires_resolved_at_and_summary(self):
        item = self.make_request(status=ServiceRequest.Status.RESOLVED)
        with self.assertRaises(ValidationError) as caught:
            item.full_clean()
        self.assertIn("resolved_at", caught.exception.message_dict)
        self.assertIn("resolution_summary", caught.exception.message_dict)
    def test_closed_requires_summary_even_when_resolved_at_exists(self):
        item = self.make_request(status=ServiceRequest.Status.CLOSED, resolved_at=timezone.now())
        with self.assertRaises(ValidationError):
            item.full_clean()
    def test_resolved_with_date_and_summary_is_valid(self):
        item = self.make_request(status=ServiceRequest.Status.RESOLVED, resolved_at=timezone.now(), resolution_summary="Socket replaced and tested.")
        item.full_clean()
    def test_due_date_filter_returns_earlier_request(self):
        now = timezone.now()
        earlier = self.make_request(title="Earlier", due_at=now - timedelta(hours=1))
        self.make_request(title="Later", due_at=now + timedelta(hours=1))
        self.assertEqual(list(ServiceRequest.objects.filter(due_at__lt=now)), [earlier])
    def test_category_in_use_is_protected(self):
        from django.db.models import ProtectedError
        self.make_request()
        with self.assertRaises(ProtectedError):
            self.category.delete()
    def test_one_work_order_per_request(self):
        from django.db import IntegrityError, transaction
        item = self.make_request()
        technician = User.objects.create_user(username="tech", password="pass12345")
        WorkOrder.objects.create(service_request=item, technician=technician)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(service_request=item, technician=technician)

class RequestWorkflowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.other = User.objects.create_user(username="other", password="pass12345")
        self.staff = User.objects.create_user(username="stafftech", password="pass12345", is_staff=True)
        self.category = Category.objects.create(name="Electrical")
        self.item = ServiceRequest.objects.create(requester=self.owner, category=self.category, title="Projector failure", description="No display", location="Room B12", priority=2)
    def test_list_requires_login(self):
        response = self.client.get(reverse("requests:list"))
        self.assertEqual(response.status_code, 302)
    def test_other_requester_receives_404(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("requests:detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 404)
    def test_owner_can_open_detail(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("requests:detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
    def test_non_staff_assignment_returns_403_and_no_work_order(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("requests:assign", args=[self.item.id]), {"technician": self.staff.id})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(WorkOrder.objects.filter(service_request=self.item).exists())
    def test_staff_assignment_creates_work_order_and_sets_assigned(self):
        self.item = service_request_assign(item_id=self.item.id, technician=self.staff, actor=self.staff)[0]
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, ServiceRequest.Status.ASSIGNED)
        self.assertTrue(WorkOrder.objects.filter(service_request=self.item, technician=self.staff).exists())
    def test_resolution_without_assignment_leaves_request_unchanged(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            service_request_resolve(item_id=self.item.id, actor=self.staff, work_notes="Checked", resolution_summary="Repaired")
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, ServiceRequest.Status.OPEN)
    def test_assigned_technician_can_resolve_both_records(self):
        service_request_assign(item_id=self.item.id, technician=self.staff, actor=self.staff)
        resolved = service_request_resolve(item_id=self.item.id, actor=self.staff, work_notes="Replaced cable", resolution_summary="Cable replaced and tested")
        resolved.refresh_from_db()
        resolved.work_order.refresh_from_db()
        self.assertEqual(resolved.status, ServiceRequest.Status.RESOLVED)
        self.assertIsNotNone(resolved.resolved_at)
        self.assertEqual(resolved.resolution_summary, "Cable replaced and tested")
        self.assertEqual(resolved.work_order.work_notes, "Replaced cable")
        self.assertIsNotNone(resolved.work_order.completed_at)
    def test_filtered_pagination_preserves_query_and_status(self):
        for n in range(12):
            ServiceRequest.objects.create(requester=self.owner, category=self.category, title=f"Socket repair {n}", description="Synthetic request", location="Lab", priority=2, status=ServiceRequest.Status.OPEN)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("requests:list") + "?q=Socket&status=open&page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_query"], "q=Socket&status=open")
