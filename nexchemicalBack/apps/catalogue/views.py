from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from . import services
from .models import Product

PRODUCTS_PER_PAGE = 12


def product_list(request):
    category_slug = request.GET.get("category") or None
    subcategory_slug = request.GET.get("subcategory") or None
    search = request.GET.get("q") or None
    sort = request.GET.get("sort") or None
    if sort not in services.SORT_OPTIONS:
        sort = None

    products = services.list_active_products(
        category_slug=category_slug, subcategory_slug=subcategory_slug, search=search, sort=sort
    )
    categories = services.list_categories()
    subcategories = services.list_subcategories(category_slug=category_slug)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "elided_page_range": paginator.get_elided_page_range(
            page_obj.number, on_each_side=1, on_ends=1
        ),
        "categories": categories,
        "subcategories": subcategories,
        "active_category": category_slug,
        "active_subcategory": subcategory_slug,
        "active_sort": sort or "",
        "sort_options": services.SORT_OPTIONS,
        "search_query": search or "",
    }
    return render(request, "catalogue/product_list.html", context)


def product_detail(request, slug):
    try:
        product = services.get_active_product(slug)
    except Product.DoesNotExist:
        raise Http404("Product not found")

    return render(request, "catalogue/product_detail.html", {"product": product})
