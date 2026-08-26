from django.core.exceptions import ValidationError
from django.db import models


class CompanyInfo(models.Model):
    """Singleton: only one row should ever exist. Also drives the homepage hero and footer."""

    phone_number = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    google_map_embed_url = models.URLField(
        "Google Maps embed URL",
        help_text='The src URL from Google Maps "Embed a map" iframe, shown on the contact page.',
    )

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    hero_heading = models.CharField(max_length=200, blank=True)
    hero_subheading = models.CharField(max_length=300, blank=True)
    hero_image = models.ImageField(upload_to="hero/", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "company info"

    def __str__(self):
        return "Company Info"

    def clean(self):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValidationError(
                "Company info already exists — edit the existing entry instead of adding a new one."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RegionalOffice(models.Model):
    """One card in the 'Our Regional Presence' grid, e.g. North America / Europe / Asia Pacific."""

    region_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "region_name"]

    def __str__(self):
        return self.region_name


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.created_at:%Y-%m-%d})"
