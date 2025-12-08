from django.urls import path
from . import views

urlpatterns = [
    # Главная — каталог
    path('', views.product_list, name='product_list'),

    # Авторизация
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # Заказы
    path('order/new/', views.create_order, name='create_order'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),

    # PDF накладная
    path('order/<int:order_id>/invoice.pdf', views.invoice_pdf, name='invoice_pdf'),

    # Статичные страницы
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('services/', views.services, name='services'),

    # --- PayPal ---
    # Страница начала оплаты
    path('order/<int:order_id>/paypal/', views.paypal_payment, name='paypal_payment'),

    # Страница завершения оплаты (после redirect с PayPal)
    path('order/<int:order_id>/paypal/execute/', views.paypal_execute, name='paypal_execute'),
]
