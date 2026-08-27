from django.db import models


class Certificate(models.Model):
    """A certification badge shown at the bottom of the About page."""

    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="certificates/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Partner(models.Model):
    """A partner/brand card shown in a grid below the homepage hero."""

    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="partners/")
    description = models.TextField(
        blank=True, help_text="Short description shown on the partner card."
    )
    website_url = models.URLField(blank=True, help_text="Optional link to the partner's website.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name
