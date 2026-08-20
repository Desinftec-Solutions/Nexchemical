from django.http import Http404
from django.shortcuts import render

from . import services
from .models import Product


def product_list(request):
    category_slug = request.GET.get("category") or None
    subcategory_slug = request.GET.get("subcategory") or None
    search = request.GET.get("q") or None

    products = services.list_active_products(
        category_slug=category_slug, subcategory_slug=subcategory_slug, search=search
    )
    categories = services.list_categories()
    subcategories = services.list_subcategories(category_slug=category_slug)

    context = {
        "products": products,
        "categories": categories,
        "subcategories": subcategories,
        "active_category": category_slug,
        "active_subcategory": subcategory_slug,
        "search_query": search or "",
    }
    return render(request, "catalogue/product_list.html", context)


def product_detail(request, slug):
    try:
        product = services.get_active_product(slug)
    except Product.DoesNotExist:
        raise Http404("Product not found")

    return render(request, "catalogue/product_detail.html", {"product": product})
