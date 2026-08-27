from catalogue.services import list_active_products
from django.shortcuts import render

from . import services


def home(request):
    context = {
        "featured_products": list_active_products()[:6],
        "partners": services.list_partners(),
        "partner_repeat": range(8),
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "certificates": services.list_certificates(),
    }
    return render(request, "core/about.html", context)


def service(request):
    return render(request, "core/service.html")
