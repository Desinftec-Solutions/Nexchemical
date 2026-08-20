from catalogue.services import list_active_products
from django.shortcuts import render


def home(request):
    context = {
        "featured_products": list_active_products()[:6],
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")
