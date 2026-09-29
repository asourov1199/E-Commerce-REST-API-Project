"""Small, readable DRF views for the assignment."""
from django.urls import reverse
from django.db.models.deletion import ProtectedError
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Category, Product, Order
from .permissions import IsStaffOrReadOnly
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, RegisterSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "categories": request.build_absolute_uri(reverse("category-list")),
        "products": request.build_absolute_uri(reverse("product-list")),
        "orders": request.build_absolute_uri(reverse("order-list")),
        "register": request.build_absolute_uri(reverse("register")),
        "login": request.build_absolute_uri(reverse("login")),
    })


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProtectedDeleteMixin:
    """Return a clear error when an existing order/product protects a record."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "This item is in use and cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )


class CategoryViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = None


class ProductViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["name"]
    ordering_fields = ["price", "created_at"]
    ordering = ["id"]


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        # A user can never view another customer's orders by changing the ID.
        return Order.objects.select_related("product", "user").filter(user=self.request.user)
