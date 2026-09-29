# Mini E-commerce REST API - বাংলা রান গাইড

এই ZIP-এ Django REST Framework দিয়ে বানানো সম্পূর্ণ অ্যাসাইনমেন্ট প্রজেক্ট আছে। Category ও Product CRUD, Product search/filter/price ordering/pagination, registration, token login, এবং logged-in user-এর নিজস্ব order API আছে। অতিরিক্তভাবে অর্ডার করার সময় স্টক যাচাই ও স্টক কমানো হয়।

## Windows-এ চালানোর সহজ পদ্ধতি

1. ZIP ফাইল Extract করুন। আপনার কম্পিউটারে **Python 3.10 বা পরবর্তী সংস্করণ** ইনস্টল থাকতে হবে। প্রথমবার Python প্যাকেজ ইনস্টল করার জন্য ইন্টারনেট লাগবে।
2. `START_WINDOWS.bat` ডাবল-ক্লিক করুন। এটি virtual environment তৈরি, requirements ইনস্টল, migration এবং sample data যোগ করে সার্ভার চালু করবে।
3. ব্রাউজারে `http://127.0.0.1:8000/api/` ওপেন করুন।
4. Category/Product যোগ বা পরিবর্তনের জন্য নতুন CMD খুলে প্রজেক্ট ফোল্ডারে যান, তারপর চালান:

```cmd
.venv\Scripts\python.exe manage.py createsuperuser
```

5. `http://127.0.0.1:8000/admin/` থেকে অ্যাডমিনে লগইন করুন। অথবা `POST /api/auth/login/` দিয়ে superuser token নিয়ে Postman-এ staff API টেস্ট করুন।

## Postman

`postman/` ফোল্ডারের Collection ও Environment—দুটি ফাইল Import করুন। Environment-এ নিজের `staff_username` ও `staff_password` সেট করুন। তারপর Collection-এর request-গুলো ক্রমানুসারে Run করুন। Login থেকে token এবং নতুন Category/Product/Order-এর ID স্বয়ংক্রিয়ভাবে সেভ হয়।

## টেস্ট করার কমান্ড

```cmd
.venv\Scripts\python.exe manage.py test
.venv\Scripts\python.exe manage.py check
```

ইংরেজি `README.md`-এ API endpoint, JSON request/response, permission ও GitHub-এ আপলোড করার সম্পূর্ণ নিয়ম আছে। অ্যাসাইনমেন্টে GitHub URL চাওয়া হয়েছে, তাই কোড নিজের GitHub account-এ আপলোড করে repository link জমা দিতে হবে।
