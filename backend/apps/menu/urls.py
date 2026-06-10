from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ModifierViewSet

router = DefaultRouter()
router.register(r'menu/categories', CategoryViewSet, basename='category')
router.register(r'menu/products', ProductViewSet, basename='product')
router.register(r'menu/modifiers', ModifierViewSet, basename='modifier')

urlpatterns = router.urls
