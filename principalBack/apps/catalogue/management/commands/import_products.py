import hashlib
import json
import urllib.request

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from catalogue.models import Category, Product, SubCategory

# Subcategory used when the source row has none (SubCategory is required).
FALLBACK_SUBCATEGORY = "General"

DOWNLOAD_TIMEOUT = 20
# Some CDNs reject urllib's default user agent.
DOWNLOAD_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NexChemical importer)"}


class Command(BaseCommand):
    help = (
        "Import products from a JSON dump (list of objects with id, name, "
        "cas_number, specification, category, subcategory). Idempotent: rows "
        "are keyed on a SKU derived from the source id, and re-importing "
        "updates existing products in place. Images are not imported."
    )

    def add_arguments(self, parser):
        parser.add_argument("json_path", help="Path to the JSON file to import.")
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not download image_url files into Product.image.",
        )

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
            with open(options["json_path"]) as f:
                rows = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Could not read {options['json_path']}: {exc}")

        self._image_cache = {}
        created_count = updated_count = image_count = 0
        for row in rows:
            name = (row.get("name") or "").strip()
            if not name or row.get("id") is None:
                self.stderr.write(f"skipped row without id/name: {row!r}")
                continue

            category, _ = Category.objects.get_or_create(
                name=(row.get("category") or "").strip() or "Uncategorized"
            )
            subcategory, _ = SubCategory.objects.get_or_create(
                category=category,
                name=(row.get("subcategory") or "").strip() or FALLBACK_SUBCATEGORY,
            )

            cas = (row.get("cas_number") or "").strip()
            spec = (row.get("specification") or "").strip()
            is_solution = "solution" in name.lower()

            description_parts = [name + "."]
            if spec:
                description_parts.append(f"Specification: {spec}.")
            if cas:
                description_parts.append(f"CAS No. {cas}.")

            product, created = Product.objects.update_or_create(
                sku=f"XL-{row['id']:03d}",
                defaults={
                    "name": name,
                    "subcategory": subcategory,
                    "subtitle": f"CAS {cas}" if cas else spec,
                    "description": " ".join(description_parts),
                    "registration_number": f"CAS No. {cas}" if cas else "",
                    "price": 0,
                    "unit": Product.Unit.LITER if is_solution else Product.Unit.PIECE,
                    "formulation": (
                        Product.Formulation.SOLUBLE_LIQUID
                        if is_solution
                        else Product.Formulation.OTHER
                    ),
                    "is_active": True,
                },
            )
            created_count += created
            updated_count += not created

            image_url = (row.get("image_url") or "").strip()
            if image_url and not product.image and not options["skip_images"]:
                path = self._fetch_image(image_url)
                if path:
                    # Point at the stored file directly; identical URLs share it.
                    product.image.name = path
                    product.save(update_fields=["image"])
                    image_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created_count} created, {updated_count} updated, "
                f"{image_count} images attached, "
                f"{Product.objects.count()} products total."
            )
        )
