from django.core.management.base import BaseCommand

from catalogue.models import Category, ChemicalComponent, Product, SubCategory

# Product names deliberately contain the slug keywords that
# catalogue_extras.PRODUCT_IMAGE_MAP resolves to the shipped static
# photography (aegis, naturaguard, nexusyield, nitropest, rootboost, vektor).
PRODUCTS = [
    {
        "sku": "NXC-AEG-500",
        "name": "Aegis 500 SC",
        "subtitle": "Broad-Spectrum Fungicide",
        "category": "Crop Protection",
        "subcategory": "Fungicides",
        "description": (
            "Systemic suspension concentrate fungicide delivering preventive and "
            "curative control of leaf spot, rust, and powdery mildew across cereals "
            "and row crops. Rainfast within one hour of application."
        ),
        "price": "84.50",
        "unit": Product.Unit.LITER,
        "formulation": Product.Formulation.SUSPENSION_CONCENTRATE,
        "stock_quantity": 240,
        "purity_percentage": "98.60",
        "certification_note": "Certified for European and North American markets.",
        "registration_number": "EPA Reg. No. 91234-18",
        "dosage_usage": "Apply 0.5–0.75 L/ha in 200–400 L of water at first sign of disease.\nRepeat at 14-day intervals; maximum 3 applications per season.",
        "components": [("Azoxystrobin", "500 g/L (41.7% w/w)"), ("Inert co-formulants", "q.s. to 1 L")],
    },
    {
        "sku": "NXC-NGD-090",
        "name": "NaturaGuard EC",
        "subtitle": "Botanical Insect Repellent",
        "category": "Crop Protection",
        "subcategory": "Insecticides",
        "is_bio_rational": True,
        "description": (
            "Neem-derived emulsifiable concentrate that disrupts feeding and molting "
            "of soft-bodied insects while sparing beneficial pollinators. Approved "
            "for use in certified organic production."
        ),
        "price": "56.00",
        "unit": Product.Unit.LITER,
        "formulation": Product.Formulation.EMULSIFIABLE_CONCENTRATE,
        "stock_quantity": 180,
        "purity_percentage": "92.00",
        "certification_note": "OMRI listed for organic production.",
        "registration_number": "EPA Reg. No. 91234-22",
        "dosage_usage": "Dilute 5 mL per litre of water and spray to full coverage at dusk.\nReapply every 7–10 days during active infestation.",
        "components": [("Azadirachtin", "9 g/L (0.9% w/w)"), ("Cold-pressed neem oil", "850 g/L")],
    },
    {
        "sku": "NXC-NXY-200",
        "name": "NexusYield WP",
        "subtitle": "Micronutrient Yield Enhancer",
        "category": "Plant Nutrition",
        "subcategory": "Foliar Nutrients",
        "description": (
            "Wettable powder blend of chelated zinc, boron, and manganese engineered "
            "to correct hidden micronutrient deficiencies during critical growth "
            "stages and lift marketable yield."
        ),
        "price": "39.90",
        "unit": Product.Unit.KILOGRAM,
        "formulation": Product.Formulation.WETTABLE_POWDER,
        "stock_quantity": 320,
        "registration_number": "Fertilizer License FL-2024-0871",
        "dosage_usage": "Foliar spray 2.5 kg/ha at tillering and again at flowering.\nCompatible with most common tank-mix partners; jar-test before mixing.",
        "components": [("Zinc (EDTA-chelated)", "120 g/kg"), ("Boron", "40 g/kg"), ("Manganese", "60 g/kg")],
    },
    {
        "sku": "NXC-NTP-250",
        "name": "NitroPest 250 EC",
        "subtitle": "Contact & Stomach Insecticide",
        "category": "Crop Protection",
        "subcategory": "Insecticides",
        "description": (
            "Fast-acting emulsifiable concentrate for control of chewing and sucking "
            "pests in vegetables, cotton, and orchards. Strong knockdown with "
            "residual protection of up to three weeks."
        ),
        "price": "72.25",
        "unit": Product.Unit.LITER,
        "formulation": Product.Formulation.EMULSIFIABLE_CONCENTRATE,
        "stock_quantity": 150,
        "purity_percentage": "97.40",
        "registration_number": "EPA Reg. No. 91234-31",
        "dosage_usage": "Apply 0.4–0.6 L/ha; do not exceed 2 applications per crop cycle.\nObserve a 14-day pre-harvest interval.",
        "components": [("Lambda-cyhalothrin", "250 g/L (23.5% w/w)")],
    },
    {
        "sku": "NXC-RTB-050",
        "name": "RootBoost GR",
        "subtitle": "Microbial Soil Conditioner",
        "category": "Plant Nutrition",
        "subcategory": "Bio Fertilizers",
        "is_bio_rational": True,
        "description": (
            "Granular consortium of mycorrhizal fungi and nitrogen-fixing bacteria "
            "that regenerates soil biology, improves root architecture, and reduces "
            "synthetic fertilizer demand by up to 30%."
        ),
        "price": "44.00",
        "unit": Product.Unit.KILOGRAM,
        "formulation": Product.Formulation.GRANULE,
        "stock_quantity": 400,
        "certification_note": "Compatible with certified organic systems.",
        "registration_number": "Biostimulant Reg. BS-2025-114",
        "dosage_usage": "Broadcast 25 kg/ha at planting and incorporate into the top 10 cm of soil.\nStore in a cool, dry place; living product — use within 12 months.",
        "components": [("Rhizophagus irregularis", "1×10⁴ propagules/g"), ("Azospirillum brasilense", "1×10⁸ CFU/g")],
    },
    {
        "sku": "NXC-VKT-075",
        "name": "Vektor 75 WP",
        "subtitle": "Systemic Seed-Borne Disease Control",
        "category": "Crop Protection",
        "subcategory": "Fungicides",
        "description": (
            "Wettable powder seed treatment protecting cereals against smut, bunt, "
            "and seedling blight. Uniform coverage with low dust-off for safer "
            "on-farm handling."
        ),
        "price": "61.75",
        "unit": Product.Unit.KILOGRAM,
        "formulation": Product.Formulation.WETTABLE_POWDER,
        "stock_quantity": 90,
        "purity_percentage": "99.10",
        "registration_number": "EPA Reg. No. 91234-07",
        "dosage_usage": "Slurry-treat seed at 150 g per 100 kg of seed before sowing.\nTreated seed must not be used for food or feed.",
        "components": [("Carboxin", "375 g/kg (37.5% w/w)"), ("Thiram", "375 g/kg (37.5% w/w)")],
    },
    {
        "sku": "NXC-SLV-990",
        "name": "NexSolv 99",
        "subtitle": "High-Purity Process Solvent",
        "category": "Industrial Chemicals",
        "subcategory": "Solvents & Intermediates",
        "description": (
            "Technical-grade isopropyl alcohol produced under ISO 9001 controls for "
            "formulation, extraction, and surface-preparation processes that demand "
            "consistent, low-water solvent quality."
        ),
        "price": "28.40",
        "unit": Product.Unit.LITER,
        "formulation": Product.Formulation.SOLUBLE_LIQUID,
        "stock_quantity": 600,
        "purity_percentage": "99.80",
        "certification_note": "Batch-certified with full CoA traceability.",
        "registration_number": "REACH Reg. 01-2119457558-25",
        "dosage_usage": "Use undiluted or dilute to process specification.\nHandle in ventilated areas away from ignition sources; see SDS.",
        "components": [("Isopropyl alcohol", "≥ 99.8% v/v"), ("Water", "≤ 0.2% v/v")],
    },
]


class Command(BaseCommand):
    help = "Seed the catalogue with sample categories, subcategories, and products. Idempotent."

    def handle(self, *args, **options):
        created_count = 0
        for spec in PRODUCTS:
            category, _ = Category.objects.get_or_create(name=spec["category"])
            subcategory, _ = SubCategory.objects.get_or_create(
                category=category, name=spec["subcategory"]
            )

            components = spec.get("components", [])
            defaults = {
                k: v
                for k, v in spec.items()
                if k not in ("sku", "category", "subcategory", "components")
            }
            defaults["subcategory"] = subcategory

            product, created = Product.objects.get_or_create(
                sku=spec["sku"], defaults=defaults
            )
            if created:
                created_count += 1
                for order, (name, amount) in enumerate(components):
                    ChemicalComponent.objects.create(
                        product=product, name=name, amount=amount, order=order
                    )
            self.stdout.write(
                f"{'created' if created else 'exists '}  {product.sku}  {product.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created_count} products created, "
                f"{Category.objects.count()} categories, "
                f"{Product.objects.count()} products total."
            )
        )
