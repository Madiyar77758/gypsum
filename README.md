# Gypsum Inventory

Order and stock management web app for a building-materials business (gypsum products), built with Django. Customers browse a catalog and place orders; the owner gets a Telegram notification, a PDF invoice and a ready-made admin panel for stock and orders.

## Features

- **Catalog** with search by name and description, product photos and units
- **Public order form** (no account needed) with delivery address; order status and payment status tracking
- **Telegram notification** for every new order. Best effort: a Telegram outage never loses the order
- **PDF invoice** per order (ReportLab)
- **PayPal sandbox payments**: create payment, redirect, execute, mark the order as paid
- **User registration and login**
- **Django admin** for products, warehouse stock and orders, with filters, search, date hierarchy, bulk PDF invoices and **CSV export**
- **Contact form** that sends e-mail through SMTP

## Stack

Python · Django 5.2 · SQLite · Pillow · ReportLab · python-telegram-bot · PayPal REST SDK. Deployed on Render.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the catalog and http://127.0.0.1:8000/admin/ for the admin panel. Add a few products there first.

## Configuration

All secrets come from environment variables; see [`.env.example`](.env.example). None of them is required for local development. Without a Telegram token notifications are skipped, without PayPal keys the payment button reports an error, without SMTP credentials the contact form cannot send.

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` | Django core settings |
| `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `HOST_URL` | Hosting and PayPal return URLs |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | New-order notifications |
| `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` | PayPal sandbox |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `SUPPORT_EMAIL` | Contact form SMTP |

## Data model

`Product` (name, price, unit, image) · `Warehouse` (product, quantity in stock) · `Order` (client, product, quantity, delivery address, status: pending / shipped / completed / cancelled, payment status: unpaid / paid, `total_price`).

## Roadmap

Automatic stock deduction on order, PostgreSQL in production, per-user order history, automated tests.
