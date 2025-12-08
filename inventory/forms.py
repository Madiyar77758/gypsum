from django import forms
from .models import Order


# --- Форма заказа (для администратора) ---
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client_name", "product", "quantity", "delivery_address"]  # Добавлено поле адреса
        labels = {
            "client_name": "Имя клиента",
            "product": "Товар",
            "quantity": "Количество",
            "delivery_address": "Адрес доставки"  # Лейбл для нового поля
        }
        widgets = {
            "client_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите имя клиента"
            }),
            "product": forms.Select(attrs={
                "class": "form-select"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "delivery_address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Введите адрес доставки",
                "rows": 3
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }


# --- Публичная форма заказа (для клиентов) ---
class PublicOrderForm(forms.ModelForm):
    """Используется на сайте, без выбора статуса"""
    class Meta:
        model = Order
        fields = ["client_name", "quantity", "delivery_address"]  # Убрали поле выбора товара
        labels = {
            "client_name": "Имя клиента",
            "quantity": "Количество",
            "delivery_address": "Адрес доставки"  # Лейбл для нового поля
        }
        widgets = {
            "client_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите имя клиента"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "delivery_address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Введите адрес доставки",
                "rows": 3
            }),
        }


# --- Форма обратной связи ---
class ContactForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        max_length=80,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@gmail.com'
        })
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__'
        })
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите ваше сообщение...'
        })
    )
