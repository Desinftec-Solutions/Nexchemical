from rest_framework.routers import DefaultRouter

from .api_views import CategoryViewSet, ProductViewSet, SubCategoryViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("subcategories", SubCategoryViewSet, basename="subcategory")

urlpatterns = router.urls
