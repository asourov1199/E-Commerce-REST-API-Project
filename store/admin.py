from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "total_price", "order_date")
    list_filter = ("order_date",)
    search_fields = ("user__username", "product__name")
    readonly_fields = ("user", "product", "quantity", "total_price", "order_date")

    def has_add_permission(self, request):
        return False  # Orders should be created via the API so stock is deducted.

    def has_change_permission(self, request, obj=None):
        return False
