"""Optional sample catalogue for manual/Postman testing."""
from decimal import Decimal
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add a small demo catalogue. Safe to run more than once."

    def handle(self, *args, **options):
        examples = {
            "Electronics": [
                ("Wireless Mouse", "Compact USB wireless mouse", "750.00", 20),
                ("Smart Phone", "128 GB smartphone", "18500.00", 8),
                ("USB-C Cable", "One meter USB-C charging cable", "350.00", 30),
            ],
            "Books": [
                ("Django for Beginners", "Introduction to Django", "950.00", 12),
                ("Python Notebook", "Practice exercises and notes", "200.00", 25),
            ],
            "Fashion": [
                ("Cotton T-shirt", "Comfortable everyday t-shirt", "650.00", 15),
            ],
        }
        for category_name, products in examples.items():
            category, _ = Category.objects.get_or_create(name=category_name)
            for name, description, price, stock in products:
                Product.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={"description": description, "price": Decimal(price), "stock": stock},
                )
        self.stdout.write(self.style.SUCCESS("Demo catalogue is ready."))
