from django import template
from django.templatetags.static import static as static_url

register = template.Library()

# Deterministic slug-keyword -> original static frontend asset mapping.
# The product catalogue photography was shipped as static design assets
# (static/img/product-*.jpg) before the ImageField upload workflow existed,
# so we key off the product slug instead of relying on an uploaded file.
PRODUCT_IMAGE_MAP = {
    "aegis": "img/product-aegis.jpg",
    "naturaguard": "img/product-naturaguard.jpg",
    "nexusyield": "img/product-nexusyield.jpg",
    "nitropest": "img/product-nitropest.jpg",
    "rootboost": "img/product-rootboost.jpg",
    "vektor": "img/product-vektor.jpg",
}

DETAIL_HERO_FALLBACK = "img/detail-hero.png"


def _match_static_image(product):
    slug = (getattr(product, "slug", "") or "").lower()
    for keyword, path in PRODUCT_IMAGE_MAP.items():
        if keyword in slug:
            return path
    return None


@register.filter
def product_image(product):
    """Resolved URL for a product's card/hero photo, or None if unmapped.

    Prefers an uploaded ImageField (product.image) when present so the
    Django-driven upload path keeps working, falling back to the original
    static design asset for the products that shipped with one.
    """
    if getattr(product, "image", None):
        return product.image.url
    path = _match_static_image(product)
    return static_url(path) if path else None


@register.filter
def product_detail_image(product):
    """Same as product_image but always returns a URL, falling back to a
    generic detail hero image so the product detail page never renders an
    empty frame."""
    return product_image(product) or static_url(DETAIL_HERO_FALLBACK)
