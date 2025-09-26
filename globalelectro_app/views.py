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
                    return redirect('home')
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
    if request.method == 'POST':
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

        category = get_object_or_404(Category, pk=category_id)

        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            condition=condition,
            stock_quantity=stock_quantity,
            category=category,
            image=image if image else None,
            is_featured=is_featured
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

    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'dashboard/product_list.html', {'products': products, 'categories': categories})

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
@admin_required
def order_list(request):
    orders = CustomerOrder.objects.all().order_by('-created_at')
    return render(request, 'dashboard/order_list.html', {'orders': orders})
#======== cart =======
@csrf_exempt


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
            return JsonResponse({"success": True, "message": "Added to cart (DB)"})

        # Session cart للمستخدمين غير المسجلين
        session_cart = request.session.get("cart", {})
        if str(product_id) in session_cart:
            session_cart[str(product_id)] += quantity
        else:
            session_cart[str(product_id)] = quantity
        request.session["cart"] = session_cart
        return JsonResponse({"success": True, "message": "Added to cart (Session)"})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# عرض الكارت
def view_cart(request):

    cart_items = []
    total = 0

    # لو المستخدم مسجل دخول، جلب الكارت من DB
    if request.user.is_authenticated:
        try:
            user = Users.objects.get(email=request.user.email)
        except Users.DoesNotExist:
            user = None

        if user:
            items = CartItem.objects.filter(user=user)
            for item in items:
                item_total = item.product.price * item.quantity
                total += item_total
                cart_items.append({
                    "product": item.product,
                    "quantity": item.quantity,
                    "item_total": item_total,
                    "cart_item_id": item.cart_item_id 

                })

    # لو غير مسجل، جلب الكارت من Session
    else:
        session_cart = request.session.get("cart", {})
        for product_id, quantity in session_cart.items():
            if not str(product_id).isdigit():
                continue
            product = get_object_or_404(Product, pk=int(product_id))
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total,
                
            })

    context = {
        "cart_items": cart_items,
        "total": total
    }
    return render(request, "cart/cart.html", context)

# ===== Helpers =====
def merge_session_cart(request):
    # جلب السلة من الجلسة
    session_cart = request.session.get('cart', {})

    if not request.user.is_authenticated:
        return  # إذا المستخدم مش مسجل، ما نعمل شي

    user = request.user

    for product_id, item_data in session_cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # إذا المنتج غير موجود، نتخطاه

        quantity = item_data.get('quantity', 1)  # افتراضي 1 إذا ما موجود

        # استخدام get_or_create مع defaults لتفادي NullError
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # لو العنصر موجود مسبقًا، نجمع الكميات
            cart_item.quantity += quantity
            cart_item.save()

    # بعد الدمج، ننظف السلة من الجلسة
    request.session['cart'] = {}
    request.session.modified = True
def delete_cart_item(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    return redirect('cart') 
