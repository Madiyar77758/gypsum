import asyncio
from telegram import Bot
from django.conf import settings


TELEGRAM_BOT_TOKEN = '8329428347:AAGykJ_dmnRkICyNJkUlnMJ8b0Z6VOx7uNg'
TELEGRAM_CHAT_ID = '5725971435'     


# Асинхронная функция для отправки сообщений
async def send_telegram_message(order):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Иконки для сообщения
    emoji_new_order = "🆕"  # Иконка нового
    emoji_order_id = "🔢"  # Иконка номера
    emoji_client = "👤"  # Иконка клиента
    emoji_product = "📦"  # Иконка товара
    emoji_quantity = "🔢"  # Иконка количества
    emoji_address = "🏠"  # Иконка адреса
    emoji_status = "✅"  # Иконка статуса

    message = (
        f"{emoji_new_order} *Новый заказ!*\n\n"
        f"{emoji_order_id} *Номер заказа*: #{order.pk}\n"
        f"{emoji_client} *Клиент*: {order.client_name}\n"
        f"{emoji_product} *Товар*: {order.product.name}\n"
        f"{emoji_quantity} *Количество*: {order.quantity} {order.product.unit}\n"
        f"{emoji_address} *Адрес доставки*: {order.delivery_address}\n"
        f"{emoji_status} *Статус*: {order.status}\n"
    )

    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
