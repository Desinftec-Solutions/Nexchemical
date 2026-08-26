from rest_framework import viewsets

from . import services
from .models import Category
from .serializers import CategorySerializer, ProductSerializer, SubCategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return services.list_active_products(
            category_slug=self.request.query_params.get("category"),
            subcategory_slug=self.request.query_params.get("subcategory"),
            search=self.request.query_params.get("q"),
        )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubCategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        return services.list_subcategories(category_slug=self.request.query_params.get("category"))
