from django.db import models
from django.utils import timezone


# ----- ТОВАРЫ -----
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")
    unit = models.CharField(max_length=20, default="шт.", verbose_name="Единица измерения")
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )

    def __str__(self):
        return f"{self.name} — {self.price} тг/{self.unit}"

    def get_image_url(self):
        """Возвращает ссылку на изображение или стандартную заглушку"""
        if self.image:
            return self.image.url
        return "/static/default_product_image.jpg"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


# ----- СКЛАД -----
class Warehouse(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity_in_stock = models.PositiveIntegerField(verbose_name="Количество на складе")

    def __str__(self):
        return f"{self.product.name} — {self.quantity_in_stock} {self.product.unit}"

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склад"


# ----- ЗАКАЗЫ -----
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'В обработке'),
        ('Shipped', 'Отгружен'),
        ('Completed', 'Завершён'),
        ('Cancelled', 'Отменён'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Не оплачен'),
        ('Paid', 'Оплачен'),
    ]

    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Статус заказа"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Unpaid',
        verbose_name="Статус оплаты"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата оформления")
    delivery_address = models.CharField(max_length=255, verbose_name="Адрес доставки")

    @property
    def total_price(self):
        """Возвращает общую стоимость заказа (цена * количество)"""
        return self.product.price * self.quantity

    def __str__(self):
        return f"Заказ #{self.pk} — {self.client_name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
