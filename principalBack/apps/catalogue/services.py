from .models import Category, Product, SubCategory


def list_active_products(category_slug=None, subcategory_slug=None, search=None):
    products = Product.objects.filter(is_active=True).select_related("subcategory__category")

    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    elif category_slug:
        products = products.filter(subcategory__category__slug=category_slug)

    if search:
        products = products.filter(name__icontains=search)

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
