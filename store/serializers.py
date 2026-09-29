"""Turn model instances into JSON, and validate incoming API data."""
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .models import Category, Product, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    stock = serializers.IntegerField(min_value=0)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category", "category_name", "created_at"]
        read_only_fields = ["id", "created_at", "category_name"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Order
        fields = ["id", "user", "product", "product_name", "quantity", "total_price", "order_date"]
        read_only_fields = ["id", "user", "product_name", "total_price", "order_date"]

    def create(self, validated_data):
        product = validated_data["product"]
        quantity = validated_data["quantity"]

        # Check and deduct stock in the same transaction to avoid overselling.
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=product.pk)
            updated = Product.objects.filter(pk=product.pk, stock__gte=quantity).update(
                stock=F("stock") - quantity
            )
            if not updated:
                raise serializers.ValidationError({"quantity": "Not enough stock available."})
            return Order.objects.create(
                user=self.context["request"].user,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity,
            )
