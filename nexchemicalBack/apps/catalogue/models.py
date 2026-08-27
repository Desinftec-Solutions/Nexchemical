from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "subcategories"
        ordering = ["category__name", "name"]
        unique_together = [["category", "name"]]

    def __str__(self):
        return f"{self.category.name} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)


class Product(models.Model):
    class Unit(models.TextChoices):
        LITER = "l", _("Liter")
        MILLILITER = "ml", _("Milliliter")
        KILOGRAM = "kg", _("Kilogram")
        GRAM = "g", _("Gram")
        PIECE = "pc", _("Piece")

    class Formulation(models.TextChoices):
        SUSPENSION_CONCENTRATE = "sc", _("Suspension Concentrate")
        EMULSIFIABLE_CONCENTRATE = "ec", _("Emulsifiable Concentrate")
        WETTABLE_POWDER = "wp", _("Wettable Powder")
        GRANULE = "gr", _("Granule")
        SOLUBLE_LIQUID = "sl", _("Soluble Liquid")
        OTHER = "other", _("Other")

    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200, help_text="Canonical name, used for the slug and admin.")
    name_en = models.CharField("Name (English)", max_length=200, blank=True)
    name_az = models.CharField("Name (Azerbaijani)", max_length=200, blank=True)
    name_ru = models.CharField("Name (Russian)", max_length=200, blank=True)
    subtitle = models.CharField(
        max_length=200, blank=True, help_text='Short tagline, e.g. "Advanced Fungicide".'
    )
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField("SKU", max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=2, choices=Unit.choices, default=Unit.PIECE)
    formulation = models.CharField(
        max_length=10, choices=Formulation.choices, default=Formulation.OTHER
    )
    is_bio_rational = models.BooleanField(
        default=False, help_text='Shows a "Bio-Rational" badge on the catalogue card.'
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    purity_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='e.g. 99.8 for "99.8% Pure".',
    )
    certification_note = models.CharField(
        max_length=255,
        blank=True,
        help_text='e.g. "Certified for European and North American Markets."',
    )
    registration_number = models.CharField(max_length=100, blank=True)
    dosage_usage = models.TextField(blank=True, help_text="Application rate / usage instructions.")
    sds_file = models.FileField(
        "SDS document", upload_to="sds/", blank=True, null=True, help_text="Safety Data Sheet PDF."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def localized_name(self):
        by_language = {"en": self.name_en, "az": self.name_az, "ru": self.name_ru}
        return by_language.get(get_language()) or self.name

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def category(self):
        return self.subcategory.category


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ChemicalComponent(models.Model):
    """A row in a product's chemical composition table, e.g. 'Azoxystrobin — 500 g/kg (50% w/w)'."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="chemical_components"
    )
    name = models.CharField(max_length=150)
    amount = models.CharField(max_length=100, help_text='e.g. "500 g/kg (50% w/w)".')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.product.name})"
