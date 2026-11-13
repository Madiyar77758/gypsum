from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import asyncio
import logging
import telegram
import paypalrestsdk

from .forms import ContactForm, OrderForm, PublicOrderForm
from .models import Order, Product, Warehouse

logger = logging.getLogger(__name__)

# Django Auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# --------------------------------------------------------------------------
#  Telegram — асинхронная отправка заказов
# --------------------------------------------------------------------------
async def send_telegram_message(order):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return  # notifications are optional: configured via environment variables
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    chat_id = settings.TELEGRAM_CHAT_ID

    message = (
        f"Новый заказ!\n\n"
        f"Номер: #{order.pk}\n"
        f"Клиент: {order.client_name}\n"
        f"Товар: {order.product.name}\n"
        f"Количество: {order.quantity} {order.product.unit}\n"
        f"Адрес: {order.delivery_address}\n"
        f"Статус: {order.status}"
    )

    await bot.send_message(chat_id=chat_id, text=message)


# --------------------------------------------------------------------------
#  Каталог товаров (главная)
# --------------------------------------------------------------------------
def product_list(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        if not products.exists():
            messages.info(request, f"По запросу «{query}» ничего не найдено.")

    return render(request, "inventory/product_list.html", {
        "products": products,
        "q": query,
    })


# --------------------------------------------------------------------------
#  Создание заказа (публичная форма)
# --------------------------------------------------------------------------
def create_order(request):
    if request.method == "POST":
        form = PublicOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            product_id = request.GET.get("product_id")
            if product_id:
                try:
                    product = get_object_or_404(Product, id=product_id)
                    order.product = product
                except ObjectDoesNotExist:
                    messages.error(request, "Ошибка: товар не найден!")
                    return redirect("product_list")

            order.save()

            # Telegram notification (best effort: an outage must not lose the order)
            try:
                asyncio.run(send_telegram_message(order))
            except Exception:
                logger.exception("Telegram notification failed for order %s", order.pk)

            messages.success(request, f"Заказ №{order.pk} оформлен!")
            return redirect("order_success", order_id=order.pk)
    else:
        form = PublicOrderForm()

    return render(request, "inventory/create_order.html", {"form": form})


# --------------------------------------------------------------------------
#  Страница "Заказ оформлен"
# --------------------------------------------------------------------------
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "inventory/order_success.html", {"order": order})


# --------------------------------------------------------------------------
#  Авторизация пользователя
# --------------------------------------------------------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("product_list")

        messages.error(request, "❌ Неверный логин или пароль!")

    return render(request, "inventory/login.html")


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Пароли не совпадают!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь уже существует!")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("product_list")

    return render(request, "inventory/register.html")


def logout_user(request):
    logout(request)
    return redirect("product_list")


# --------------------------------------------------------------------------
#  Статичные страницы
# --------------------------------------------------------------------------
def about(request):
    return render(request, "inventory/about.html")


def contacts(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            subject = f"Сообщение с сайта от {data['name']}"
            body = (
                f"Имя: {data['name']}\n"
                f"E-mail: {data['email']}\n"
                f"Тел: {data.get('phone', '-')}\n\n"
                f"Сообщение:\n{data['message']}"
            )

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Спасибо! Сообщение отправлено.")
            return redirect("contacts")

    else:
        form = ContactForm()

    return render(request, "inventory/contacts.html", {"form": form})


def services(request):
    return render(request, "inventory/services.html")


# --------------------------------------------------------------------------
#  PDF накладная
# --------------------------------------------------------------------------
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False


def invoice_pdf(request, order_id):
    if not REPORTLAB_OK:
        messages.error(request, "Установите пакет reportlab.")
        return redirect("order_success", order_id=order_id)

    order = get_object_or_404(Order, pk=order_id)

    response = HttpResponse(content_type="application/pdf")
    filename = f"invoice_order_{order_id}.pdf"
    response["Content-Disposition"] = f'inline; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)
    W, H = A4
    margin = 20 * mm
    y = H - margin

    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, y, "НАКЛАДНАЯ / INVOICE")
    y -= 15 * mm

    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, f"Заказ № {order.pk}")
    y -= 6 * mm

    p.setFont("Helvetica", 10)
    p.drawString(margin, y, f"Клиент: {order.client_name}")
    y -= 6 * mm
    p.drawString(margin, y, f"Статус: {order.status}")
    y -= 10 * mm

    # Таблица
    p.setFont("Helvetica-Bold", 10)
    cols = [margin, margin + 90 * mm, margin + 120 * mm, margin + 150 * mm, W - margin]
    headers = ["Товар", "Ед.", "Кол-во", "Цена", "Сумма"]

    for i, h in enumerate(headers):
        p.drawString(cols[i], y, h)
    y -= 14 * mm

    p.setFont("Helvetica", 10)
    name = order.product.name
    unit = order.product.unit
    qty = int(order.quantity)
    price = Decimal(order.product.price)
    total = price * qty

    p.drawString(cols[0], y, name)
    p.drawString(cols[1], y, unit)
    p.drawString(cols[2], y, str(qty))
    p.drawString(cols[3], y, f"{price:.2f}")
    p.drawString(cols[4], y, f"{total:.2f}")
    y -= 15 * mm

    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(cols[4], y, f"ИТОГО: {total:.2f} тг")

    p.showPage()
    p.save()

    return response


# ==========================================================================
#                         🟦 PAYPAL — ДОБАВЛЕНО ЗДЕСЬ 🟦
# ==========================================================================

# Конфигурация PayPal
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


# --- Создание платежа ---
def paypal_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    total_price = order.product.price * order.quantity

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": f"{settings.HOST_URL}/order/{order.id}/paypal/execute/",
            "cancel_url": f"{settings.HOST_URL}/order/{order.id}/success/",
        },
        "transactions": [{
            "amount": {
                "total": f"{order.total_price:.2f}",
                "currency": "USD"
            },
            "description": f"Оплата заказа №{order.id}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)

    messages.error(request, "Ошибка при создании платежа PayPal")
    return redirect("order_success", order_id=order.id)


# Подтверждение оплаты
def paypal_execute(request, order_id):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        order = get_object_or_404(Order, pk=order_id)
        order.status = "Completed"  # Ставим статус заказа как "Завершён"
        order.payment_status = "Paid"
        order.payment_id = payment_id
        order.save()

        messages.success(request, "Платеж успешно выполнен!")
        return redirect("order_success", order_id=order.id)

    messages.error(request, "Ошибка при подтверждении оплаты")
    return redirect("order_success", order_id=order_id)
