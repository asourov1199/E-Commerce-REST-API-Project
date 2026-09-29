# Mini E-commerce REST API

This is my Django REST Framework assignment project. It is a small backend for an online shop where customers can browse products, search and filter the catalogue, log in with a token, and place orders. Staff can manage categories and products. I used SQLite to keep local setup simple.

The submitted ZIP includes the complete source, the initial migration, automated API tests, a sample catalogue command, a Postman collection, and Windows setup instructions.

## 1. Technology

- Python 3.10 or newer
- Django 5.2 LTS
- Django REST Framework 3.16
- django-filter 25.x
- SQLite (included with Python; the database is created by migrations)
- DRF Token Authentication

## 2. Run it locally

**Windows quick start:** Extract the ZIP and double-click `START_WINDOWS.bat`. On the first run it creates `.venv`, installs packages, applies migrations, adds sample products, and starts the development server. An internet connection is needed to install the Python packages the first time.

**Manual commands (Windows PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

If PowerShell blocks activation, run `.venv\Scripts\python.exe` instead of `python` for each command, or use Command Prompt and `.venv\Scripts\activate.bat`.

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/api/` for the API root or `http://127.0.0.1:8000/admin/` for the Django admin panel. `createsuperuser` is needed to make a staff account for catalogue changes. Do **not** use the development server for public production traffic.

## 3. API endpoints

All API URLs end with a trailing slash. `GET` catalogue endpoints are public; write requests require a staff user's token.

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/api/` | API links | Public |
| POST | `/api/auth/register/` | Register a customer | Public |
| POST | `/api/auth/login/` | Log in and receive a token | Public |
| GET, POST | `/api/categories/` | List / create categories | Public GET / staff POST |
| GET, PUT, PATCH, DELETE | `/api/categories/<id>/` | Category detail / edit / delete | Public GET / staff write |
| GET, POST | `/api/products/` | List / create products | Public GET / staff POST |
| GET, PUT, PATCH, DELETE | `/api/products/<id>/` | Product detail / edit / delete | Public GET / staff write |
| GET, POST | `/api/orders/` | List my orders / place order | Login required |
| GET | `/api/orders/<id>/` | View one of my orders | Owner only |

Users cannot view orders belonging to other accounts. Orders cannot be edited or deleted through the API.

### Register and log in

Register with `POST /api/auth/register/`:

```json
{
  "username": "student1",
  "email": "student1@example.com",
  "password": "StudentPass123!"
}
```

Log in with `POST /api/auth/login/`:

```json
{
  "username": "student1",
  "password": "StudentPass123!"
}
```

The response contains a token:

```json
{"token": "your-generated-token"}
```

For all protected requests, add the header:

```text
Authorization: Token your-generated-token
```

Token authentication accepts the **username** and password. A staff/superuser account also logs in using the same endpoint and then uses its token for category and product changes.

### Create a category (staff)

`POST /api/categories/`

```json
{"name": "Electronics"}
```

### Add a product (staff)

`POST /api/products/`

```json
{
  "name": "Wireless Mouse",
  "description": "Compact wireless mouse",
  "price": "750.00",
  "stock": 20,
  "category": 1
}
```

Product details include `id`, `name`, `description`, `price`, `stock`, `category`, `category_name`, and `created_at`. Prices are stored as decimal values, not floating-point numbers.

### Search, filter, order, and paginate products

```text
GET /api/products/?search=phone
GET /api/products/?category=1
GET /api/products/?price=750.00
GET /api/products/?min_price=500&max_price=1000
GET /api/products/?ordering=price
GET /api/products/?ordering=-price
GET /api/products/?page=2
GET /api/products/?page_size=10
GET /api/products/?search=phone&category=1&ordering=price
```

Product pagination returns `count`, `next`, `previous`, and `results`. The default page size is 5; you can request up to 100 using `page_size`.

### Place an order (customer token)

`POST /api/orders/`

```json
{"product": 1, "quantity": 2}
```

Example response (IDs, dates, and prices depend on your data):

```json
{
  "id": 1,
  "user": "student1",
  "product": 1,
  "product_name": "Wireless Mouse",
  "quantity": 2,
  "total_price": "1500.00",
  "order_date": "2026-09-25T14:00:00+06:00"
}
```

The server, not the client, sets the `user`, calculates the `total_price`, records the `order_date`, and deducts stock. The price is saved at the time of the order, so later product price changes do not alter existing orders. An invalid quantity or insufficient stock returns HTTP 400. Deleting a category with products or a product that belongs to an order returns HTTP 409.

## 4. Postman testing

1. Import `postman/Mini_Ecommerce_REST_API.postman_collection.json` as a Collection.
2. Import `postman/Local.postman_environment.json` as an Environment and select it.
3. First run migrations and create a staff account using `python manage.py createsuperuser`.
4. Enter your staff username and password in the environment variables `staff_username` and `staff_password`.
5. Run the Collection in order: register -> customer login -> staff login -> category/product requests -> order requests. Login scripts automatically save `token` and `staff_token`; create scripts save the new IDs.
6. Before running the whole collection a second time, use fresh values for `username`/`email` and new names for the sample categories/products, or reset the local database. There is no need to publish or commit real tokens or passwords.

Some API operations intentionally return errors to demonstrate validation, such as ordering more items than the available stock. The collection includes checks for their expected HTTP status codes.

## 5. Automated testing

```bash
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

The test suite covers registration, login, category and product CRUD, staff permissions, search/filter/order/pagination, user-specific orders, stock validation, price snapshot, and deletion protection. No live API keys or payment gateway are needed.

## 6. Project structure

```text
mini_ecommerce_assignment/
├── manage.py
├── requirements.txt
├── mini_ecommerce/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── store/
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/0001_initial.py
│   ├── management/commands/seed_demo.py
│   └── tests/test_api.py
├── postman/
│   ├── Mini_Ecommerce_REST_API.postman_collection.json
│   └── Local.postman_environment.json
├── START_WINDOWS.bat
├── README_BN.md
└── ASSIGNMENT_REPORT.md
```

## 7. Submitting to GitHub

The assignment sheet requests a GitHub URL, so upload this extracted folder to **your own GitHub repository**. From the project folder:

```bash
git init
git add .
git commit -m "Complete mini e-commerce REST API assignment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mini-ecommerce-rest-api.git
git push -u origin main
```

Create the empty repository on GitHub first and replace `YOUR_USERNAME`. Do not upload `.venv/`, `db.sqlite3`, `.env`, or actual passwords or tokens; the `.gitignore` already excludes these. Submit the GitHub repository link requested in the assignment.

## 8. Notes

This is a learning project, not a production checkout system. Real deployments require a properly configured secret key, HTTPS, restricted hosts, production database setup, logging, throttling, and payment integration. `DEBUG` defaults to `True` **for local use only**.
