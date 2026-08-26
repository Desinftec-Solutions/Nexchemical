from rest_framework import serializers

from .models import Category, ChemicalComponent, Product, ProductImage, SubCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = ["id", "name", "slug", "category"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "order"]


class ChemicalComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChemicalComponent
        fields = ["id", "name", "amount", "order"]


class ProductSerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer(read_only=True)
    gallery_images = ProductImageSerializer(many=True, read_only=True)
    chemical_components = ChemicalComponentSerializer(many=True, read_only=True)
    formulation_display = serializers.CharField(source="get_formulation_display", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "subtitle",
            "slug",
            "sku",
            "subcategory",
            "description",
            "price",
            "unit",
            "formulation",
            "formulation_display",
            "is_bio_rational",
            "stock_quantity",
            "in_stock",
            "image",
            "gallery_images",
            "is_active",
            "purity_percentage",
            "certification_note",
            "registration_number",
            "dosage_usage",
            "sds_file",
            "chemical_components",
            "created_at",
            "updated_at",
        ]
