from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import CartItem, Product

@receiver(user_logged_in)
def merge_session_cart(sender, user, request, **kwargs):
    session_cart = request.session.get("cart", {})
    for product_id, qty in session_cart.items():
        product = Product.objects.get(pk=int(product_id))
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += qty
        else:
            cart_item.quantity = qty
        cart_item.save()
    request.session["cart"] = {}  # مسح session بعد المزامنة
