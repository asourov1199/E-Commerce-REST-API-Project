from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import api_root, CategoryViewSet, ProductViewSet, OrderViewSet, RegisterView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", obtain_auth_token, name="login"),
    path("", include(router.urls)),
]
