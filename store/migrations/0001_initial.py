# Generated-style initial migration; committed so students only need `migrate`.
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "categories"},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0.01"))])),
                ("stock", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="store.category")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(validators=[MinValueValidator(1)])),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("order_date", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="store.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-order_date", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=models.Q(price__gt=0), name="product_price_positive"),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(condition=models.Q(quantity__gte=1), name="order_quantity_positive"),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(condition=models.Q(total_price__gte=0), name="order_total_nonnegative"),
        ),
    ]
