import hashlib
import json
import urllib.request
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from catalogue.models import Category, ChemicalComponent, Product, SubCategory

# All rows land under this single catalogue category.
DEFAULT_CATEGORY = "Kimyəvi yuyucu xammallar"

# Data dump shipped with the app; used when no json_path is given.
DEFAULT_JSON_PATH = Path(__file__).resolve().parents[2] / "data" / "hexakimya_products.json"

# Surfactant class detected in the source "category_breadcrumb" -> subcategory
# name. Order matters: the first keyword found wins. Anything unmatched falls
# back to FALLBACK_SUBCATEGORY.
SUBCATEGORY_RULES = [
    ("amphoteric", "Amfoter səthi-aktiv maddələr"),
    ("cationic", "Kation səthi-aktiv maddələr"),
    ("non-ionic", "Qeyri-ionik səthi-aktiv maddələr"),
    ("nonionic", "Qeyri-ionik səthi-aktiv maddələr"),
    ("anionic", "Anion səthi-aktiv maddələr"),
]
FALLBACK_SUBCATEGORY = "Digər xammallar"

DOWNLOAD_TIMEOUT = 20
# Some CDNs reject urllib's default user agent.
DOWNLOAD_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NexChemical importer)"}


class Command(BaseCommand):
    help = (
        "Import detergent raw-material products from the hexakimya JSON dump "
        "(list of objects with id, name, category_breadcrumb, specifications, "
        "description, image_url). Idempotent: rows are keyed on a SKU derived "
        "from the source id (HX-###), so re-importing updates in place."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            nargs="?",
            default=str(DEFAULT_JSON_PATH),
            help="Path to the JSON file to import (defaults to the bundled data dump).",
        )
        parser.add_argument(
            "--category",
            default=DEFAULT_CATEGORY,
            help=f'Catalogue category to file the products under (default: "{DEFAULT_CATEGORY}").',
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not download image_url files into Product.image.",
        )

    def _subcategory_name(self, breadcrumb):
        haystack = (breadcrumb or "").lower()
        for keyword, name in SUBCATEGORY_RULES:
            if keyword in haystack:
                return name
        return FALLBACK_SUBCATEGORY

    def _fetch_image(self, url):
        """Download url once per run; identical URLs share one stored file.

        Returns the storage path for Product.image, or None on failure.
        """
        if url in self._image_cache:
            return self._image_cache[url]

        ext = url.rsplit(".", 1)[-1].lower()
        if ext not in ("jpg", "jpeg", "png", "webp"):
            ext = "jpg"
        path = f"products/{hashlib.sha1(url.encode()).hexdigest()}.{ext}"

        if not default_storage.exists(path):
            try:
                req = urllib.request.Request(url, headers=DOWNLOAD_HEADERS)
                with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
                    data = resp.read()
                path = default_storage.save(path, ContentFile(data))
            except OSError as exc:
                self.stderr.write(f"image download failed for {url}: {exc}")
                path = None

        self._image_cache[url] = path
        return path

    def handle(self, *args, **options):
        try:
            with open(options["json_path"], encoding="utf-8") as f:
                rows = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Could not read {options['json_path']}: {exc}")

        category, _ = Category.objects.get_or_create(name=options["category"].strip())

        self._image_cache = {}
        created_count = updated_count = image_count = 0
        for row in rows:
            name = (row.get("name") or "").strip()
            if not name or row.get("id") is None:
                self.stderr.write(f"skipped row without id/name: {row!r}")
                continue

            subcategory, _ = SubCategory.objects.get_or_create(
                category=category,
                name=self._subcategory_name(row.get("category_breadcrumb")),
            )

            specs = row.get("specifications") or {}
            description = (row.get("description") or "").strip() or f"{name}."

            product, created = Product.objects.update_or_create(
                sku=f"HX-{row['id']:03d}",
                defaults={
                    "name": name,
                    "name_en": name,
                    "slug": f"{slugify(name)}-hx-{row['id']}",
                    "subcategory": subcategory,
                    "description": description,
                    "price": 0,
                    "unit": Product.Unit.KILOGRAM,
                    "formulation": Product.Formulation.OTHER,
                    "is_active": True,
                },
            )
            created_count += created
            updated_count += not created

            # Rebuild the composition table from the source specs dict so
            # re-imports stay in sync instead of piling up duplicate rows.
            product.chemical_components.all().delete()
            ChemicalComponent.objects.bulk_create(
                ChemicalComponent(product=product, name=key, amount=str(value), order=order)
                for order, (key, value) in enumerate(specs.items())
            )

            image_url = (row.get("image_url") or "").strip()
            if image_url and not product.image and not options["skip_images"]:
                path = self._fetch_image(image_url)
                if path:
                    product.image.name = path
                    product.save(update_fields=["image"])
                    image_count += 1

        total = Product.objects.filter(subcategory__category=category).count()
        message = (
            f"Done: {created_count} created, {updated_count} updated, "
            f"{image_count} images attached, "
            f'{total} products under "{category.name}".'
        )
        try:
            self.stdout.write(self.style.SUCCESS(message))
        except UnicodeEncodeError:
            # Some Windows consoles can't encode the category name (cp1252).
            self.stdout.write(self.style.SUCCESS(message.encode("ascii", "replace").decode()))
