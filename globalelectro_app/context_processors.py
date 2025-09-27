# globalelectro_app/context_processors.py
from .models import CartItem, Users
from django.db.models import Sum

from .models import CartItem

def cart_items_count(request):
    user_id = request.session.get("user_id")
    count = 0
    if user_id:
        # عدد المنتجات المختلفة في السلة للمستخدم
        count = CartItem.objects.filter(user_id=user_id).count()
    else:
        # عدد المنتجات في session cart
        session_cart = request.session.get("cart", {})
        count = len(session_cart)
    return {"cart_count": count}