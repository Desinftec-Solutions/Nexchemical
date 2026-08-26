from pathlib import Path

from catalogue.models import Category, ChemicalComponent, Product, ProductImage, SubCategory
from contact.models import CompanyInfo, RegionalOffice
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

PRODUCTS_DIR = Path(settings.BASE_DIR) / "static" / "img" / "products"

PRODUCTS_DATA = [
    dict(
        subcategory=("Crop Protection", "Insecticide"),
        name="Aegis Spectrum",
        subtitle="Broad-spectrum systemic insecticide",
        sku="AS-001",
        formulation="sc",
        price="38.00",
        stock_quantity=140,
        description="Broad-spectrum systemic insecticide for control across major row crops.",
        image_file="aegis-spectrum.png",
    ),
    dict(
        subcategory=("Crop Protection", "Insecticide"),
        name="Vektor Elite",
        subtitle="Targeted foliar insecticide",
        sku="VE-002",
        formulation="ec",
        price="42.50",
        stock_quantity=95,
        description="Targeted foliar treatment for fast knockdown of resistant insect pests.",
        image_file="vektor-elite.png",
    ),
    dict(
        subcategory=("Crop Protection", "Insecticide"),
        name="NitroPest-X 500",
        subtitle="High-efficacy foliar insecticide",
        sku="NPX-500",
        formulation="sc",
        price="46.00",
        stock_quantity=60,
        description="Targeted foliar treatment for high-pressure pest outbreaks in field crops.",
        image_file="nitropest-x-500.png",
    ),
    dict(
        subcategory=("Crop Protection", "Herbicide"),
        name="NexusYield Pro™",
        subtitle="Broad-spectrum systemic herbicide",
        sku="NYP-003",
        formulation="sc",
        price="39.75",
        stock_quantity=110,
        description="Broad-spectrum systemic herbicide for pre- and post-emergent weed control.",
        image_file="nexusyield-pro.png",
    ),
    dict(
        subcategory=("Bio-Based Solutions", "Bio-Insecticide"),
        name="NaturaGuard",
        subtitle="Naturally derived bio-insecticide",
        sku="NG-004",
        formulation="wp",
        price="34.00",
        stock_quantity=75,
        is_bio_rational=True,
        description="Naturally derived formulation with high efficacy against soft-bodied pests.",
        image_file="naturaguard.png",
    ),
    dict(
        subcategory=("Bio-Based Solutions", "Bio-Insecticide"),
        name="RootBoost Plus",
        subtitle="Naturally derived soil bio-insecticide",
        sku="RBP-005",
        formulation="wp",
        price="29.50",
        stock_quantity=88,
        is_bio_rational=True,
        description="Naturally derived formulation for soil-borne pests and root health support.",
        image_file="rootboost-plus.png",
    ),
    dict(
        subcategory=("Crop Protection", "Fungicide"),
        name="Vita-Grow 500WP",
        subtitle="Advanced Fungicide",
        sku="VG-500WP",
        formulation="wp",
        price="45.00",
        stock_quantity=120,
        description=(
            "High-performance wettable powder for precision control of soil-borne pathogens. "
            "Engineered for large-scale operations requiring stringent safety standards."
        ),
        image_file="vita-grow-500wp.png",
        purity_percentage="99.80",
        certification_note="Certified for European and North American Markets.",
        registration_number="REG-2026-0042",
        dosage_usage=(
            "Apply 2-3 kg/ha diluted in 300-500L water per hectare. Repeat every 10-14 days as "
            "needed, up to 4 applications per season."
        ),
        chemical_components=[
            ("Azoxystrobin", "500 g/kg (50% w/w)"),
            ("Surfactant Matrix", "120 g/kg"),
            ("Inert Carriers", "to 1.0 kg"),
        ],
    ),
]

REGIONAL_OFFICES = [
    dict(
        region_name="North America",
        order=1,
        address="8800 Nexus Way, Suite 400, Houston, TX 77002, USA",
        phone_number="+1 (713) 555-0100",
        email="na-sales@nexchemical.com",
    ),
    dict(
        region_name="Europe",
        order=2,
        address="Chemical Park B44, 67056 Ludwigshafen, Germany",
        phone_number="+49 621 555-0200",
        email="eu-reg@nexchemical.com",
    ),
    dict(
        region_name="Asia Pacific",
        order=3,
        address="Level 18, IFC Tower 2, Central, Hong Kong",
        phone_number="+852 2555-0300",
        email="ap-tech@nexchemical.com",
    ),
    dict(
        region_name="Latin America",
        order=4,
        address="Av. das Nações Unidas, 14171, São Paulo, SP, Brazil",
        phone_number="+55 11 555-0400",
        email="latam@nexchemical.com",
    ),
]


class Command(BaseCommand):
    help = (
        "Seeds the database with the NexChemical demo catalog, company info, and regional offices."
    )

    def handle(self, *args, **options):
        ChemicalComponent.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        SubCategory.objects.all().delete()
        Category.objects.all().delete()
        RegionalOffice.objects.all().delete()
        CompanyInfo.objects.all().delete()

        subcategory_cache = {}

        def get_subcategory(category_name, subcategory_name):
            key = (category_name, subcategory_name)
            if key not in subcategory_cache:
                category, _ = Category.objects.get_or_create(name=category_name)
                subcategory_cache[key] = SubCategory.objects.create(
                    category=category, name=subcategory_name
                )
            return subcategory_cache[key]

        for data in PRODUCTS_DATA:
            data = dict(data)
            image_file = data.pop("image_file")
            components = data.pop("chemical_components", [])
            category_name, subcategory_name = data.pop("subcategory")
            data["subcategory"] = get_subcategory(category_name, subcategory_name)

            product = Product.objects.create(**data)
            image_path = PRODUCTS_DIR / image_file
            with open(image_path, "rb") as f:
                product.image.save(image_file, File(f), save=True)

            for order, (name, amount) in enumerate(components, start=1):
                ChemicalComponent.objects.create(
                    product=product, name=name, amount=amount, order=order
                )

        CompanyInfo.objects.create(
            phone_number="+1 (713) 555-0100",
            email="na-sales@nexchemical.com",
            address="8800 Nexus Way, Suite 400, Houston, TX 77002, USA",
            google_map_embed_url="https://www.google.com/maps?q=8800+Nexus+Way+Houston+TX+77002&output=embed",
            facebook_url="https://facebook.com/nexchemical",
            instagram_url="https://instagram.com/nexchemical",
            linkedin_url="https://linkedin.com/company/nexchemical",
            hero_heading="Pioneering Chemistry for a Sustainable Future",
            hero_subheading=(
                "Bridging the gap between laboratory innovation and agricultural excellence "
                "with regulatory-compliant chemical solutions."
            ),
        )

        for office in REGIONAL_OFFICES:
            RegionalOffice.objects.create(**office)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Category.objects.count()} categories, "
                f"{SubCategory.objects.count()} subcategories, "
                f"{Product.objects.count()} products, "
                f"{RegionalOffice.objects.count()} offices."
            )
        )
