from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from .models import *  
from django.http import JsonResponse


# ===== ديكوريتور للتحقق من الدور =====
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    return wrapper
# ===== الفيوز العامة =====
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def login_register(request):
    return render(request, "login_register.html")

# ===== إدارة المستخدمين =====
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
            # role='customer'  # افتراضي
        )

        request.session['first_name'] = user.first_name
        request.session['user_id'] = user.user_id
        request.session['role'] = user.role

        messages.success(request, "Account created & logged in successfully", extra_tags='register')
        return redirect('home')

    return redirect('login_register')


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = Users.objects.get(email=email)
            if check_password(password, user.password):
               
                request.session['first_name'] = user.first_name
                request.session['user_id'] = user.user_id
                request.session['role'] = user.role

                messages.success(request, "Logged in successfully", extra_tags='login')

                
                if user.role == 'admin':
                    return redirect('admin_dashboard')  
                else:
                    return redirect('home')

            else:
                messages.error(request, "Incorrect password", extra_tags='login')
        except Users.DoesNotExist:
            messages.error(request, "Email not found", extra_tags='login')

    return redirect('login_register')


def logout_user(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('home')

# ===== فيو داشبورد الادمن =====
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
    if request.method == "POST":
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
    if request.method == "POST":
        try:
            category = Category.objects.get(pk=category_id)
            category.delete()
            return JsonResponse({"status": "success"})
        except Category.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Category not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Category

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from django.http import JsonResponse
from .models import Product, Category, Users, CustomerOrder

# ===== ديكوريتور للتحقق من الدور =====
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role')
        if role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    return wrapper

# ===== الفيوز العامة =====
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def login_register(request):
    return render(request, "login_register.html")

# ===== إدارة المستخدمين =====
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

        messages.success(request, "Account created & logged in successfully", extra_tags='register')
        return redirect('home')
    return redirect('login_register')

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = Users.objects.get(email=email)
            if check_password(password, user.password):
                request.session['first_name'] = user.first_name
                request.session['user_id'] = user.user_id
                request.session['role'] = user.role
                messages.success(request, "Logged in successfully", extra_tags='login')
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Incorrect password", extra_tags='login')
        except Users.DoesNotExist:
            messages.error(request, "Email not found", extra_tags='login')
    return redirect('login_register')

def logout_user(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('home')

# ===== داشبورد الادمن =====
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

# ===== الكاتيجوري =====
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
    if request.method == "POST":
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
    if request.method == "POST":
        try:
            category = Category.objects.get(pk=category_id)
            category.delete()
            return JsonResponse({"status": "success"})
        except Category.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Category not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})




# ===== Product list + Add =====
# ===== Product list + Add =====
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
            image=image if image else None
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
            "image": product.image.url if product.image else ""
        })

    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'dashboard/product_list.html', {'products': products, 'categories': categories})


# ===== Product edit =====
@admin_required
def product_edit(request, product_id):
    if request.method == "GET":
        try:
            product = Product.objects.get(pk=product_id)
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
                "image": product.image.url if product.image else ""
            })
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})

    elif request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        condition = request.POST.get('condition', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '').strip()
        category_id = request.POST.get('category', '').strip()
        image = request.FILES.get('image')

        if not all([name, description, price, condition, stock_quantity]):
            return JsonResponse({"status": "error", "message": "All fields are required"})

        try:
            product = Product.objects.get(pk=product_id)

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
            product.save()

            return JsonResponse({"status": "success", "message": "Product updated"})
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})

    return JsonResponse({"status": "error", "message": "Invalid request"})


# ===== Product delete =====
@admin_required
def product_delete(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return JsonResponse({"status": "success", "message": "Product deleted"})
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

@admin_required
def order_list(request):
    orders = CustomerOrder.objects.all().order_by('-created_at')
    return render(request, 'dashboard/order_list.html', {'orders': orders})


@admin_required
def user_list(request):
    users = Users.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users})

@admin_required
def user_add(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'customer')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        hashed_pw = make_password(password)

        Users.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pw,
            role=role,
            phone=phone,
            address=address
        )
        messages.success(request, f"User '{first_name} {last_name}' added successfully.")
        return redirect('user_list')

    return render(request, 'dashboard/user_add.html')