from django.contrib import admin

from .models import CompanyInfo, ContactMessage, RegionalOffice


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "email", "address", "updated_at"]
    fieldsets = (
        (
            "Contact details",
            {"fields": ("phone_number", "email", "address", "google_map_embed_url")},
        ),
        ("Social links", {"fields": ("facebook_url", "instagram_url", "linkedin_url")}),
        ("Homepage hero", {"fields": ("hero_heading", "hero_subheading", "hero_image")}),
    )

    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()


@admin.register(RegionalOffice)
class RegionalOfficeAdmin(admin.ModelAdmin):
    list_display = ["region_name", "address", "phone_number", "email", "order"]
    list_editable = ["order"]
    search_fields = ["region_name", "address"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone_number", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    list_editable = ["is_read"]
    search_fields = ["full_name", "email", "phone_number", "message"]
    readonly_fields = ["full_name", "email", "phone_number", "message", "created_at"]

    def has_add_permission(self, request):
        return False
