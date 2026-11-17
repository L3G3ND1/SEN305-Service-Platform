from django.shortcuts import render
from requests_app.models import ServiceRequest

def home(request):
    active_requests = ServiceRequest.objects.exclude(status__in=[ServiceRequest.Status.RESOLVED, ServiceRequest.Status.CLOSED]).count()
    return render(request, "core/home.html", {"headline": "Report and track maintenance requests", "active_requests": active_requests})

def about(request):
    return render(request, "core/about.html", {"project_roles": ["Requester", "Coordinator", "Technician", "Administrator"]})

def contact(request):
    return render(request, "core/contact.html")

def workflow(request):
    return render(request, "core/workflow.html")
