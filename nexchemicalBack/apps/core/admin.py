from django.contrib import admin

from .models import Certificate, Partner


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    list_editable = ["order"]
    search_fields = ["name"]


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["name", "website_url", "order"]
    list_editable = ["order"]
    search_fields = ["name"]
