import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Allows ?category=1, ?price=499.99, ?min_price=100&max_price=1000.
    category = django_filters.NumberFilter(field_name="category_id")
    price = django_filters.NumberFilter(field_name="price")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "price", "min_price", "max_price"]
