from rest_framework import serializers

from .models import CompanyInfo, ContactMessage, RegionalOffice


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "full_name", "email", "phone_number", "message", "created_at"]
        read_only_fields = ["id", "created_at"]


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = [
            "phone_number",
            "email",
            "address",
            "google_map_embed_url",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "hero_heading",
            "hero_subheading",
            "hero_image",
        ]


class RegionalOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalOffice
        fields = ["id", "region_name", "address", "phone_number", "email"]
