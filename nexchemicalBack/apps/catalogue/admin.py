from django.contrib import admin
from django.utils.html import format_html

from .models import Category, ChemicalComponent, Product, ProductImage, SubCategory


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ChemicalComponentInline(admin.TabularInline):
    model = ChemicalComponent
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon_preview"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    inlines = [SubCategoryInline]

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        if not obj.icon:
            return "—"
        return format_html(
            '<img src="{}" style="height:28px;width:28px;object-fit:contain;">', obj.icon.url
        )


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "slug"]
    list_filter = ["category"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "category__name"]
    autocomplete_fields = ["category"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "subcategory",
        "sku",
        "price",
        "formulation",
        "is_bio_rational",
        "stock_quantity",
        "is_active",
    ]
    list_filter = [
        "subcategory__category",
        "subcategory",
        "formulation",
        "is_bio_rational",
        "is_active",
    ]
    list_editable = ["price", "stock_quantity", "is_active"]
    search_fields = ["name", "sku", "description", "registration_number"]
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["subcategory"]
    inlines = [ProductImageInline, ChemicalComponentInline]

    fieldsets = (
        (
            None,
            {"fields": ("subcategory", "name", "subtitle", "slug", "sku", "description", "image")},
        ),
        (
            "Translations",
            {
                "fields": ("name_en", "name_az", "name_ru"),
                "description": "Optional per-language names shown on the site. Falls back to Name above when blank.",
            },
        ),
        (
            "Pricing & stock",
            {"fields": ("price", "unit", "formulation", "stock_quantity", "is_active")},
        ),
        (
            "Regulatory & composition",
            {
                "fields": (
                    "is_bio_rational",
                    "purity_percentage",
                    "certification_note",
                    "registration_number",
                    "dosage_usage",
                    "sds_file",
                ),
            },
        ),
    )


admin.site.site_header = "NexChemical Admin"
