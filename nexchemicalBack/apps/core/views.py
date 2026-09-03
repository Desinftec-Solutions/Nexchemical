from catalogue.services import list_active_products, list_categories
from django.shortcuts import render

from . import services

# Beyond this many, the homepage category strip switches from a plain row
# to a paged slider (see .categories__strip / categories-slider.js).
CATEGORY_STRIP_VISIBLE = 6


def _category_chips(categories):
    """Pair each category with a hue evenly spread across the full color
    wheel by its position, so the homepage strip's auto-colored badges stay
    visually distinct no matter how many categories exist — add or remove
    one and every badge respaces itself automatically."""
    total = len(categories)
    return [
        {"category": category, "hue": round(360 * index / total)}
        for index, category in enumerate(categories)
    ]


def home(request):
    categories = list(list_categories())
    context = {
        "featured_products": list_active_products()[:6],
        "partners": services.list_partners(),
        "partner_repeat": range(8),
        "category_chips": _category_chips(categories),
        "category_strip_is_slider": len(categories) > CATEGORY_STRIP_VISIBLE,
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "certificates": services.list_certificates(),
    }
    return render(request, "core/about.html", context)


def service(request):
    # Unrouted for now — see apps/core/urls.py.
    return render(request, "core/service.html")
