from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, SubCategory

SORT_OPTIONS = {
    "price_asc": ("price", _("Price: Low to High")),
    "price_desc": ("-price", _("Price: High to Low")),
    "newest": ("-created_at", _("Newest")),
    "name": ("name", _("Name: A-Z")),
}


def list_active_products(category_slug=None, subcategory_slug=None, search=None, sort=None):
    products = Product.objects.filter(is_active=True).select_related("subcategory__category")

    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    elif category_slug:
        products = products.filter(subcategory__category__slug=category_slug)

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(name_en__icontains=search)
            | Q(name_az__icontains=search)
            | Q(name_ru__icontains=search)
            # CAS numbers are stored inside registration_number (e.g. "CAS No. 139-33-3"),
            # so searching "139-33-3" matches products by CAS number too.
            | Q(registration_number__icontains=search)
        )

    sort_field = SORT_OPTIONS.get(sort, (None, None))[0]
    if sort_field:
        products = products.order_by(sort_field)

    return products


def get_active_product(slug):
    return (
        Product.objects.select_related("subcategory__category")
        .prefetch_related("gallery_images", "chemical_components")
        .get(slug=slug, is_active=True)
    )


def list_categories():
    return Category.objects.all()


def list_subcategories(category_slug=None):
    subcategories = SubCategory.objects.select_related("category")
    if category_slug:
        subcategories = subcategories.filter(category__slug=category_slug)
    return subcategories
