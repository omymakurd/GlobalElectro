from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from django.http import JsonResponse
from .models import *
import secrets
import string
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.db.models import Sum
from django.db.models import F
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
import requests
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import F, DecimalField, ExpressionWrapper
from django.core.cache import cache
from django.conf import settings

from django.http import JsonResponse
from .models import CustomerOrder
from .emails import send_order_email


# ===== Helpers =====
def generate_strong_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ===== Decorators =====
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    return wrapper

# ===== General Views =====
def home(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-product_id')[:8]

    return render(request, "home.html", {
        "featured_products": featured_products
    })

def login_register(request):
    return render(request, "login_register.html")

def logout_user(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('home')

# ===== User Management =====
def create_user(request):
    if request.method == 'POST':
        errors = Users.objects.user_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value, extra_tags='register')
            return redirect('login_register')

        password = make_password(request.POST.get('password'))
        user = Users.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=password,
            phone=request.POST['phone'],
            address=request.POST['address'],
        )

        request.session['first_name'] = user.first_name
        request.session['user_id'] = user.user_id
        request.session['role'] = user.role
        
        merge_session_cart(request)
        messages.success(request, "Account created & logged in successfully", extra_tags='register')
        return redirect('home')
    return redirect('login_register')

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        users = Users.objects.filter(email=email)
        if users.exists():
            user = users.first()
            if check_password(password, user.password):
                request.session['first_name'] = user.first_name
                request.session['user_id'] = user.user_id
                request.session['role'] = user.role
                merge_session_cart(request)
                print("SESSION NOW:", dict(request.session))

                messages.success(request, "Logged in successfully", extra_tags='login')
                
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                messages.error(request, "Incorrect password", extra_tags='login')
        else:
            messages.error(request, "Email not found", extra_tags='login')
    return redirect('login_register')

@admin_required
def user_list(request):

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        role = request.POST.get("role", "customer")
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if Users.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already exists!"})

        password_plain = generate_strong_password()
        if not all([first_name, last_name, email, role,password_plain]):
            return JsonResponse({"status": "error", "message": "All fields are required"})
        
        user = Users.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password_plain),
            role=role,
            phone=phone,
            address=address,
        )

        return JsonResponse({
            "status": "success",
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
            "address": user.address,
            "password": password_plain
        })

    users = Users.objects.all()
    return render(request, "dashboard/user_list.html", {"users": users})

# ===== Admin Dashboard =====
@admin_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_users = Users.objects.count()
    total_orders = CustomerOrder.objects.count()
    latest_orders = CustomerOrder.objects.all().order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'latest_orders': latest_orders,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

# ===== Category Management =====
@admin_required
def category_list(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            category = Category.objects.create(name=name)
            return JsonResponse({"status": "success", "category_id": category.category_id, "name": category.name})
        return JsonResponse({"status": "error", "message": "Name is required"})

    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})

@admin_required
def category_edit(request, category_id):
    if request.method == 'POST':
        name = request.POST.get("name", "").strip()
        if name:
            try:
                category = Category.objects.get(pk=category_id)
                category.name = name
                category.save()
                return JsonResponse({"status": "success", "name": category.name})
            except Category.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Category not found"})
        return JsonResponse({"status": "error", "message": "Name is required"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

@admin_required
def category_delete(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(pk=category_id)
            category.delete()
            return JsonResponse({"status": "success"})
        except Category.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Category not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

# ===== Product Management =====
@admin_required
def product_list(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, pk=user_id)

    if request.method == 'POST':
        # إضافة منتج جديد
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        condition = request.POST.get('condition', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '').strip()
        category_id = request.POST.get('category', '').strip()
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') in ["true", "1", "on", "yes"]

        if not all([name, description, price, condition, stock_quantity, category_id]):
            return JsonResponse({"status": "error", "message": "All fields are required"})

        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Price and Stock must be numbers"})

        category = get_object_or_404(Category, pk=category_id)

        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            condition=condition,
            stock_quantity=stock_quantity,
            category=category,
            image=image if image else None,
            is_featured=is_featured,
            user=user
        )

        return JsonResponse({
            "status": "success",
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "condition": product.condition,
            "stock_quantity": product.stock_quantity,
            "category_id": category.category_id,
            "category_name": category.name,
            "image": product.image.url if product.image else "",
            "is_featured": product.is_featured
        })

    # ===== عرض المنتجات مع فلترة اختيارية =====
    filter_mine = request.GET.get('filter_mine')  # إذا موجود، فلترة لمنتجات الأدمن فقط
    if filter_mine == '1':
        products = Product.objects.filter(user=user).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')

    categories = Category.objects.all()
    return render(request, 'dashboard/product_list.html', {
        'products': products,
        'categories': categories,
        'filter_mine': filter_mine
    })

@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'GET':
        category = product.category
        return JsonResponse({
            "status": "success",
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "condition": product.condition,
            "stock_quantity": product.stock_quantity,
            "category_id": category.category_id if category else None,
            "category_name": category.name if category else "",
            "image": product.image.url if product.image else "",
            "is_featured": product.is_featured
            

        })

    elif request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        condition = request.POST.get('condition', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '').strip()
        category_id = request.POST.get('category', '').strip()
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') in ["true", "1", "on", "yes"]

        if not all([name, description, price, condition, stock_quantity]):
            return JsonResponse({"status": "error", "message": "All fields are required"})

        if category_id:
            category = get_object_or_404(Category, pk=category_id)
            product.category = category

        product.name = name
        product.description = description
        product.price = price
        product.condition = condition
        product.stock_quantity = stock_quantity
        if image:
            product.image = image
        product.is_featured = is_featured 
        
        product.save()

        return JsonResponse({"status": "success", "message": "Product updated"})

    return JsonResponse({"status": "error", "message": "Invalid request"})

@admin_required
def product_delete(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return JsonResponse({"status": "success", "message": "Product deleted"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

# ===== Orders =====
def order_list(request):
    # فلترة حسب البحث
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    orders = CustomerOrder.objects.all()
    
    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    orders = orders.order_by('-created_at')
    
    return render(request, 'dashboard/order_list.html', {
        'orders': orders,
        'query': query,
        'status_filter': status_filter
    })

def update_order_status(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')
        try:
            order = CustomerOrder.objects.get(order_id=order_id)
            order.status = new_status
            order.save()
            return JsonResponse({'status': 'success'})
        except CustomerOrder.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def order_details(request, order_id):
    order = get_object_or_404(CustomerOrder, order_id=order_id)
    # بيانات الطلب + المنتجات
    products = []
    for item in order.order_items.all():  # افترض وجود related_name='order_items'
        products.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': str(item.price),
            'subtotal': str(item.quantity * item.price)
        })
    data = {
        'order_id': order.order_id,
        'user': f"{order.user.first_name} {order.user.last_name}",
        'total_price': str(order.total_price),
        'status': order.status,
        'created_at': order.created_at.strftime("%Y-%m-%d %H:%M"),
        'products': products
    }
    return JsonResponse({'status': 'success', 'order': data})

def print_invoice(request, order_id):
    order = get_object_or_404(CustomerOrder, order_id=order_id)
    return render(request, 'dashboard/print_invoice.html', {'order': order})
from .emails import send_order_email
def send_order_email_view(request, order_id):
    if request.method == "POST":
        try:
            order = CustomerOrder.objects.get(order_id=order_id)
            send_order_email(order)
            return JsonResponse({"status": "success", "message": "Email sent successfully"})
        except CustomerOrder.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})
#======== cart =======



# إضافة منتج للكارت
@csrf_exempt

def add_to_cart(request):
    try:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"})

        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            quantity = 1

        if not product_id:
            return JsonResponse({"success": False, "message": "Product ID is required"})

        product = get_object_or_404(Product, pk=product_id)

        user_id = request.session.get("user_id")
        if user_id:
            user = get_object_or_404(Users, pk=user_id)
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={"quantity": quantity}  # مهم
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            cart_count = CartItem.objects.filter(user=user).aggregate(total=Sum("quantity"))["total"] or 0
            return JsonResponse({"success": True, "message": "Added to cart (DB)", "cart_count": cart_count})

        # Session cart للمستخدمين غير المسجلين
        session_cart = request.session.get("cart", {})
        if str(product_id) in session_cart:
            session_cart[str(product_id)] += quantity
        else:
            session_cart[str(product_id)] = quantity
        request.session["cart"] = session_cart
        cart_count = sum(session_cart.values())
        return JsonResponse({"success": True, "message": "Added to cart (Session)","cart_count": cart_count})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# عرض الكارت


# ===== Helpers =====
def merge_session_cart(request):
    session_cart = request.session.get('cart', {})
    user_id = request.session.get('user_id')

    if not user_id:  # إذا المستخدم مش مسجل
        return

    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return

    for product_id_str, quantity in session_cart.items():
        try:
            product_id = int(product_id_str)
            product = Product.objects.get(product_id=product_id)
        except (ValueError, Product.DoesNotExist):
            continue

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': int(quantity)}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

    # تنظيف session بعد الدمج
    request.session['cart'] = {}
    request.session.modified = True



def view_cart(request):
    user_id = request.session.get("user_id")
    cart_items = []
    total = 0

    if user_id:  # مستخدم مسجل
        cart_items = CartItem.objects.filter(user_id=user_id).annotate(
            item_total=F("quantity") * F("product__price")
        )
        total = cart_items.aggregate(total=Sum("item_total"))["total"] or 0
    else:  # زائر (Session cart)
        session_cart = request.session.get("cart", {})
        for product_id_str, quantity in session_cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.get(pk=product_id)
            except (Product.DoesNotExist, ValueError):
                continue  # تجاهل المنتج المفقود
            item_total = product.price * quantity
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total,
                "cart_item_id": None
            })
        total = sum(item["item_total"] for item in cart_items)

    return render(request, "cart/cart.html", {
        "cart_items": cart_items,
        "total": total
    })

# ==================== تحديث عنصر ====================
def update_cart_item(request, item_id):
    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        user_id = request.session.get("user_id")
        if user_id:
            # DB cart
            cart_item = get_object_or_404(CartItem, cart_item_id=item_id, user_id=user_id)
            cart_item.quantity = quantity
            cart_item.save()
        else:
            # Session cart: هنا item_id هو product_id
            session_cart = request.session.get("cart", {})
            if str(item_id) in session_cart:
                session_cart[str(item_id)] = quantity
                request.session["cart"] = session_cart
                request.session.modified = True

    return redirect("view_cart")


def update_cart_item_session(request, product_id):
    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1
        cart = request.session.get("cart", {})
        cart[str(product_id)] = quantity
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "Cart updated successfully.")
    return redirect("view_cart")

# ==================== حذف عنصر ====================
def delete_cart_item(request, item_id):
    user_id = request.session.get("user_id")
    if user_id:
        cart_item = get_object_or_404(CartItem, cart_item_id=item_id, user_id=user_id)
        cart_item.delete()
    else:
        session_cart = request.session.get("cart", {})
        if str(item_id) in session_cart:
            del session_cart[str(item_id)]
            request.session["cart"] = session_cart
            request.session.modified = True
    messages.success(request, "Item removed from cart.")
    return redirect("view_cart")


def delete_cart_item_session(request, product_id):
    session_cart = request.session.get("cart", {})
    if str(product_id) in session_cart:
        del session_cart[str(product_id)]
        request.session["cart"] = session_cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")
    return redirect("view_cart")
# ==================== Checkout (Placeholder) ====================


def login_required_custom(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            messages.error(request, "Please log in to access checkout.")
            return redirect("login_register")
        return view_func(request, *args, **kwargs)
    return wrapper

def checkout(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Please log in to access checkout.")
        return redirect("login_register")

    user = get_object_or_404(Users, pk=user_id)

    # ===== جلب Cart Items =====
    cart_items = CartItem.objects.filter(user=user).annotate(
        item_total=F("quantity") * F("product__price")
    )
    total_price = cart_items.aggregate(total=Sum("item_total"))["total"] or 0

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("view_cart")

    if request.method == "POST":
        address = request.POST.get("address", user.address)
        phone = request.POST.get("phone", user.phone)

        # ===== استخدام transaction لضمان atomicity =====
        try:
            with transaction.atomic():
                # التحقق من المخزون لكل منتج
                for item in cart_items:
                    if item.quantity > item.product.stock_quantity:
                        messages.error(
                            request,
                            f"Insufficient stock for {item.product.name}. Available: {item.product.stock_quantity}"
                        )
                        return redirect("view_cart")

                # إنشاء الطلب
                order = CustomerOrder.objects.create(
                    user=user,
                    shipping_address=address,
                    total_price=total_price,
                    status="pending",
                    created_at=timezone.now()
                )

                # تحويل CartItem → OrderItem
                order_items = []
                for item in cart_items:
                    order_items.append(
                        OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                    )
                    # تحديث مخزون المنتجات
                    item.product.stock_quantity -= item.quantity
                    item.product.save()
                OrderItem.objects.bulk_create(order_items)

                # مسح السلة
                cart_items.delete()
                request.session['cart'] = {}
                request.session.modified = True

        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect("view_cart")

        return render(request, "orders/checkout.html", {
            "cart_items": cart_items,
            "total_price": total_price,
            "user": user,
            "order_success": True,
            "order_id": order.order_id
        })
    

    return render(request, "orders/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "user": user
    })



    
def get_currency_rate(target_currency):
    if target_currency == "EGP":
        return Decimal("1.0")

    # جرب نجيب الريت من الكاش أولاً
    cache_key = f"rate_EGP_{target_currency}"
    cached_rate = cache.get(cache_key)
    if cached_rate:
        return Decimal(cached_rate)

    # لو مش موجود بالكاش، نجيب من API
    api_key = "431031410a897a7f358a951a0e52b86a"
    url = f"http://api.currencylayer.com/convert?access_key={api_key}&from=EGP&to={target_currency}&amount=1"
    try:
        response = requests.get(url, timeout=5).json()
        if response.get("success") and "info" in response:
            rate = Decimal(str(response["info"]["quote"]))
            # خزنه بالكاش لمدة 6 ساعات (21600 ثانية)
            cache.set(cache_key, rate, timeout=21600)
            return rate
    except Exception:
        pass

    # لو حصل خطأ أو API متوقف
    return Decimal("1.0")


def all_products(request):
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')
    category_name = request.GET.get('category', '')
    target_currency = request.GET.get("currency", "EGP")

    products = Product.objects.all()

    # تصفية حسب الكاتيجوري والبحث
    if category_name:
        products = products.filter(category__name=category_name)
    if search_query:
        products = products.filter(name__icontains=search_query)

    # الفرز
    if sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'price_high':
        products = products.order_by('-price')
    elif sort_option == 'price_low':
        products = products.order_by('price')
    elif sort_option == 'featured':
        products = products.order_by('-is_featured')
    else:
        products = products.order_by('name')

    # 🟢 جلب الريت باستخدام الكاش
    rate = get_currency_rate(target_currency)

    # أضف السعر المحول لكل منتج
    for product in products:
        product.converted_price = round(product.price * rate, 2)

    context = {
        'products': products,
        'search_query': search_query,
        'sort_option': sort_option,
        'category_name': category_name,
        'categories': Category.objects.all(),
        'currency': target_currency,
    }

    return render(request, 'products/all_product.html', context)
def about(request):
    return render(request, 'about.html')
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # مثال: إرسال رسالة بريد إلكتروني
        try:
            send_mail(
                f"{subject} - from {name}",
                message,
                email,  # from email
                ['omyma_1994@hotmail.com'],  # to email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except:
            messages.error(request, "Oops! Something went wrong.")

        return redirect('contact')  # يرجع نفس الصفحة بعد الإرسال

    return render(request, 'contact.html')


def login_required_custom(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            messages.error(request, "Please log in to access checkout.")
            return redirect("login_register")
        return view_func(request, *args, **kwargs)
    return wrapper



@login_required_custom
def customer_dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Please log in to access dashboard.")
        return redirect("login_register")

    custom_user = get_object_or_404(Users, pk=user_id)

    # آخر 5 أوردرات
    latest_orders = CustomerOrder.objects.filter(user=custom_user).order_by('-created_at')[:5]

    # منتجات المستخدم المشتراة
    purchased_product_ids = OrderItem.objects.filter(order__user=custom_user).values_list('product_id', flat=True)
    purchased_categories = OrderItem.objects.filter(order__user=custom_user).values_list('product__category_id', flat=True).distinct()

    # توصيات المنتجات
    recommended_products = Product.objects.filter(
        category_id__in=purchased_categories
    ).exclude(
        product_id__in=purchased_product_ids
    ).distinct()[:5]

    if not recommended_products:
        recommended_products = Product.objects.order_by('-created_at')[:5]

    context = {
        'recommended_products': recommended_products,
        'latest_orders': latest_orders,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)
