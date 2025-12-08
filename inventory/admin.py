from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
import csv

from .models import Product, Warehouse, Order


# ===== ТОВАРЫ ===============================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "unit")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_per_page = 25


# ===== СКЛАД ================================================================
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity_in_stock")
    list_display_links = ("id", "product")
    autocomplete_fields = ("product",)
    list_per_page = 25


# ===== ЗАКАЗЫ ===============================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "client_name", "product", "quantity",
        "status", "payment_status_display", "created_at", "total_amount_display", "invoice_link",
    )
    list_display_links = ("id", "client_name")
    list_filter = ("status", "created_at", "payment_status")  # Добавлено фильтрация по статусу оплаты
    search_fields = ("client_name", "product__name")
    autocomplete_fields = ("product",)
    date_hierarchy = "created_at"
    list_per_page = 25

    actions = ["download_invoice_pdf", "export_orders_csv"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product")

    # --- Сумма заказа
    def total_amount_display(self, obj: Order) -> str:
        value = obj.total_price
        return f"{value:.2f}"
    total_amount_display.short_description = "Сумма"

    # --- Статус оплаты
    def payment_status_display(self, obj: Order) -> str:
        return obj.payment_status
    payment_status_display.short_description = "Статус оплаты"

    # --- Кнопка PDF
    def invoice_link(self, obj: Order):
        url = reverse("invoice_pdf", args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">📄 PDF</a>', url)
    invoice_link.short_description = "Накладная"

    # --- Экшен: скачать PDF
    def download_invoice_pdf(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Выберите ровно один заказ для формирования PDF.",
                level=messages.ERROR
            )
            return
        order = queryset.first()
        return HttpResponseRedirect(reverse("invoice_pdf", args=[order.pk]))
    download_invoice_pdf.short_description = "Скачать накладную (PDF)"

    # --- Экспорт CSV
    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename=orders.csv"
        writer = csv.writer(response)
        writer.writerow(["ID", "Клиент", "Товар", "Кол-во", "Статус", "Статус оплаты", "Дата", "Сумма"])

        for o in queryset.select_related("product"):
            writer.writerow([
                o.id,
                o.client_name,
                o.product.name,
                o.quantity,
                o.status,
                o.payment_status,  # Добавили столбец для статуса оплаты
                o.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{o.total_price:.2f}",
            ])
        return response
    export_orders_csv.short_description = "Экспорт в CSV"
