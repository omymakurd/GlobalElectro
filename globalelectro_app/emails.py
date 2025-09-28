# globalelectro_app/emails.py
from django.core.mail import send_mail
from django.conf import settings



def send_order_email(order):
    subject = f"Order #{order.order_id} Confirmation"
    message = f"Hello {order.user.first_name},\n\nYour order has been received.\nTotal: {order.total_price}\nStatus: {order.status}"
    recipient_list = [order.user.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
