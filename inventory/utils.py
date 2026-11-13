from django.conf import settings
from telegram import Bot


async def send_telegram_message(order):
    """Send a new-order notification to the configured Telegram chat."""
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    message = (
        f"Новый заказ!\n\n"
        f"Номер заказа: #{order.pk}\n"
        f"Клиент: {order.client_name}\n"
        f"Товар: {order.product.name}\n"
        f"Количество: {order.quantity} {order.product.unit}\n"
        f"Адрес доставки: {order.delivery_address}\n"
        f"Статус: {order.status}\n"
    )
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
