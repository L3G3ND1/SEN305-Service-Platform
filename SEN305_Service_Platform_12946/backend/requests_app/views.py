from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST
from .forms import AssignmentForm, CommentForm, ResolutionForm, ServiceRequestForm
from .models import ServiceRequest
from .selectors import request_detail_for_user, request_summary_counts, visible_requests
from .services import comment_create, service_request_assign, service_request_create, service_request_resolve, service_request_update

@login_required
def request_list(request):
    qs = visible_requests(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    if status:
        qs = qs.filter(status=status)
    qs = qs.order_by("-priority", "created_at")
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    page_query = params.urlencode()
    return render(request, "requests_app/request_list.html", {
        "page_obj": page_obj, "query": query, "selected_status": status,
        "status_choices": ServiceRequest.Status.choices,
        "summary_counts": request_summary_counts(request.user), "page_query": page_query,
    })

@login_required
def request_detail(request, request_id):
    try:
        item = request_detail_for_user(request.user, request_id)
    except ServiceRequest.DoesNotExist as exc:
        raise Http404("Service request not found.") from exc
    return render(request, "requests_app/request_detail.html", {"item": item, "comments": item.comments.select_related("author"), "comment_form": CommentForm(), "assignment_form": AssignmentForm() if request.user.is_staff else None, "resolution_form": ResolutionForm() if request.user.is_staff or (hasattr(item, "work_order") and item.work_order.technician_id == request.user.pk) else None})

@login_required
def request_create(request):
    form = ServiceRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = service_request_create(requester=request.user, **form.cleaned_data)
        messages.success(request, "Service request created.")
        return redirect("requests:detail", request_id=item.id)
    return render(request, "requests_app/request_form.html", {"form": form, "mode": "Create"})

@login_required
def request_update(request, request_id):
    try:
        item = request_detail_for_user(request.user, request_id)
    except ServiceRequest.DoesNotExist as exc:
        raise Http404("Service request not found.") from exc
    if not request.user.is_staff and item.requester_id != request.user.pk:
        raise Http404("Service request not found.")
    form = ServiceRequestForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        try:
            item = service_request_update(item=item, actor=request.user, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Service request updated.")
            return redirect("requests:detail", request_id=item.id)
    return render(request, "requests_app/request_form.html", {"form": form, "mode": "Update", "item": item})

@require_POST
@login_required
def comment_add(request, request_id):
    try:
        item = request_detail_for_user(request.user, request_id)
    except ServiceRequest.DoesNotExist as exc:
        raise Http404("Service request not found.") from exc
    form = CommentForm(request.POST)
    if form.is_valid():
        comment_create(item=item, author=request.user, **form.cleaned_data)
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Enter a comment of at least 3 characters.")
    return redirect("requests:detail", request_id=item.id)

@require_POST
@login_required
def request_assign(request, request_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access required.")
    item = get_object_or_404(ServiceRequest, pk=request_id)
    form = AssignmentForm(request.POST)
    if form.is_valid():
        try:
            service_request_assign(item_id=item.id, technician=form.cleaned_data["technician"], actor=request.user)
        except ValidationError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Technician assigned.")
    else:
        messages.error(request, "Choose an active staff technician.")
    return redirect("requests:detail", request_id=item.id)

@require_POST
@login_required
def request_resolve(request, request_id):
    item = get_object_or_404(ServiceRequest, pk=request_id)
    if not request.user.is_staff and not (hasattr(item, "work_order") and item.work_order.technician_id == request.user.pk):
        return HttpResponseForbidden("Only staff or the assigned technician can resolve this request.")
    form = ResolutionForm(request.POST)
    if form.is_valid():
        try:
            service_request_resolve(item_id=item.id, actor=request.user, **form.cleaned_data)
        except ValidationError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Request resolved.")
    else:
        messages.error(request, "Provide work notes and a resolution summary.")
    return redirect("requests:detail", request_id=item.id)
