"""API tests: run with `python manage.py test`."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from store.models import Category, Order, Product


class StoreAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.electronics = Category.objects.create(name="Electronics")
        cls.books = Category.objects.create(name="Books")
        cls.phone = Product.objects.create(
            name="Smart Phone", description="Sample phone", price=Decimal("249.50"),
            stock=6, category=cls.electronics,
        )
        cls.book = Product.objects.create(
            name="Django Book", description="Sample book", price=Decimal("99.00"),
            stock=10, category=cls.books,
        )
        cls.staff = User.objects.create_user(
            username="manager", password="ManagerPass123!", is_staff=True,
        )
        cls.customer = User.objects.create_user(
            username="customer1", password="CustomerPass123!",
        )
        cls.other_customer = User.objects.create_user(
            username="customer2", password="CustomerPass123!",
        )
        cls.staff_token = Token.objects.create(user=cls.staff)
        cls.customer_token = Token.objects.create(user=cls.customer)
        cls.other_token = Token.objects.create(user=cls.other_customer)

    def login_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_api_root(self):
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("products", response.data)

    def test_categories_are_public(self):
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        detail = self.client.get(reverse("category-detail", args=[self.books.pk]))
        self.assertEqual(detail.data["name"], "Books")

    def test_only_staff_can_manage_categories(self):
        url = reverse("category-list")
        data = {"name": "Home"}
        self.assertEqual(self.client.post(url, data).status_code, 401)
        self.login_as(self.customer_token)
        self.assertEqual(self.client.post(url, data).status_code, 403)
        self.login_as(self.staff_token)
        result = self.client.post(url, data)
        self.assertEqual(result.status_code, 201)
        detail_url = reverse("category-detail", args=[result.data["id"]])
        self.assertEqual(self.client.patch(detail_url, {"name": "Home Goods"}).status_code, 200)
        self.assertEqual(self.client.delete(detail_url).status_code, 204)

    def test_duplicate_category_is_rejected(self):
        self.login_as(self.staff_token)
        response = self.client.post(reverse("category-list"), {"name": "Books"})
        self.assertEqual(response.status_code, 400)

    def test_staff_product_crud(self):
        url = reverse("product-list")
        self.login_as(self.staff_token)
        created = self.client.post(url, {
            "name": "Keyboard", "description": "Mechanical", "price": "1800.00",
            "stock": 12, "category": self.electronics.pk,
        })
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["category_name"], "Electronics")
        detail_url = reverse("product-detail", args=[created.data["id"]])
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        self.assertEqual(self.client.patch(detail_url, {"price": "1700.00"}).status_code, 200)
        self.assertEqual(self.client.delete(detail_url).status_code, 204)

    def test_non_staff_cannot_change_product(self):
        self.login_as(self.customer_token)
        response = self.client.patch(
            reverse("product-detail", args=[self.phone.pk]), {"stock": 999}
        )
        self.assertEqual(response.status_code, 403)

    def test_product_search_category_price_and_ordering(self):
        url = reverse("product-list")
        self.assertEqual(self.client.get(url, {"search": "phone"}).data["count"], 1)
        by_category = self.client.get(url, {"category": self.books.pk})
        self.assertEqual(by_category.data["count"], 1)
        self.assertEqual(by_category.data["results"][0]["name"], "Django Book")
        self.assertEqual(self.client.get(url, {"price": "249.50"}).data["count"], 1)
        self.assertEqual(self.client.get(url, {"min_price": 100, "max_price": 300}).data["count"], 1)
        asc = self.client.get(url, {"ordering": "price"}).data["results"]
        desc = self.client.get(url, {"ordering": "-price"}).data["results"]
        self.assertEqual([p["name"] for p in asc], ["Django Book", "Smart Phone"])
        self.assertEqual([p["name"] for p in desc], ["Smart Phone", "Django Book"])

    def test_product_pagination(self):
        for i in range(6):
            Product.objects.create(
                name=f"Accessory {i}", price="10.00", stock=2, category=self.electronics
            )
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.data["count"], 8)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(self.client.get(reverse("product-list"), {"page": 2}).data["results"]), 3)

    def test_invalid_product_values(self):
        self.login_as(self.staff_token)
        url = reverse("product-list")
        for changes in ({"price": "-5.00"}, {"stock": -1}):
            data = {"name": "Invalid", "price": "10.00", "stock": 1, "category": self.books.pk}
            data.update(changes)
            self.assertEqual(self.client.post(url, data).status_code, 400)

    def test_registration_and_token_login(self):
        registered = self.client.post(reverse("register"), {
            "username": "newstudent", "email": "new@example.com", "password": "GreatPassword123!"
        })
        self.assertEqual(registered.status_code, 201)
        self.assertNotIn("password", registered.data)
        self.assertTrue(User.objects.get(username="newstudent").check_password("GreatPassword123!"))
        login = self.client.post(reverse("login"), {
            "username": "newstudent", "password": "GreatPassword123!"
        })
        self.assertEqual(login.status_code, 200)
        self.assertIn("token", login.data)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(reverse("register"), {
            "username": "someone", "email": "someone@example.com", "password": "12345678"
        })
        self.assertEqual(response.status_code, 400)

    def test_orders_require_token(self):
        url = reverse("order-list")
        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(self.client.post(url, {"product": self.phone.pk, "quantity": 1}).status_code, 401)

    def test_customer_can_order_and_stock_is_deducted(self):
        self.login_as(self.customer_token)
        created = self.client.post(reverse("order-list"), {"product": self.phone.pk, "quantity": 2})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["user"], "customer1")
        self.assertEqual(created.data["total_price"], "499.00")
        self.phone.refresh_from_db()
        self.assertEqual(self.phone.stock, 4)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.client.get(reverse("order-detail", args=[created.data["id"]])).status_code, 200)

    def test_users_see_only_their_orders(self):
        self.login_as(self.customer_token)
        created = self.client.post(reverse("order-list"), {"product": self.phone.pk, "quantity": 1})
        self.login_as(self.other_token)
        self.assertEqual(self.client.get(reverse("order-list")).data["count"], 0)
        self.assertEqual(self.client.get(reverse("order-detail", args=[created.data["id"]])).status_code, 404)

    def test_invalid_quantity_and_insufficient_stock(self):
        self.login_as(self.customer_token)
        url = reverse("order-list")
        self.assertEqual(self.client.post(url, {"product": self.phone.pk, "quantity": 0}).status_code, 400)
        too_many = self.client.post(url, {"product": self.phone.pk, "quantity": 100})
        self.assertEqual(too_many.status_code, 400)
        self.assertIn("quantity", too_many.data)
        self.phone.refresh_from_db()
        self.assertEqual(self.phone.stock, 6)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_total_does_not_change_after_product_price_update(self):
        self.login_as(self.customer_token)
        created = self.client.post(reverse("order-list"), {"product": self.phone.pk, "quantity": 2})
        self.phone.price = Decimal("999.00")
        self.phone.save(update_fields=["price"])
        order = Order.objects.get(pk=created.data["id"])
        self.assertEqual(order.total_price, Decimal("499.00"))

    def test_products_and_categories_used_by_orders_are_protected(self):
        self.login_as(self.customer_token)
        self.assertEqual(self.client.post(
            reverse("order-list"), {"product": self.phone.pk, "quantity": 1}
        ).status_code, 201)
        self.login_as(self.staff_token)
        self.assertEqual(self.client.delete(reverse("product-detail", args=[self.phone.pk])).status_code, 409)
        self.assertEqual(self.client.delete(reverse("category-detail", args=[self.electronics.pk])).status_code, 409)

    def test_order_does_not_allow_update_or_delete(self):
        self.login_as(self.customer_token)
        created = self.client.post(reverse("order-list"), {"product": self.phone.pk, "quantity": 1})
        url = reverse("order-detail", args=[created.data["id"]])
        self.assertEqual(self.client.patch(url, {"quantity": 2}).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)
