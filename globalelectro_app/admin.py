from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Users, Category, Product, CartItem, CustomerOrder, OrderItem

# -------------------- Users Admin --------------------
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'user_id', 'first_name', 'last_name', 'email',
        'role', 'phone', 'address', 'created_at'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('role', 'created_at')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        # أي مستخدم جديد يتم إضافته من Admin يكون Admin تلقائي
        if not change:
            obj.role = 'admin'
        # تشفير كلمة المرور إذا لم تكن مشفرة مسبقاً
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

# -------------------- Category Admin --------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

# -------------------- Product Admin --------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 'name', 'category',
        'price', 'stock_quantity', 'condition',
        'is_featured', 'created_at'
    )
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'condition', 'is_featured')
    ordering = ('-created_at',)

# -------------------- CartItem Admin --------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_item_id', 'user', 'product', 'quantity', 'created_at')
    search_fields = ('user__email', 'product__name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# -------------------- CustomerOrder Admin --------------------
@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status', 'total_price', 'created_at')
    search_fields = ('user__email',)
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

# -------------------- OrderItem Admin --------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order_item_id', 'order', 'product',
        'quantity', 'price', 'created_at'
    )
    search_fields = ('order__order_id', 'product__name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
