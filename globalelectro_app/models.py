from django.db import models
import re
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify


class UserManager(models.Manager):
    def user_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$')

        if not postData['first_name']:
            errors["missing_first_name"] = "Please Enter a First name"
        elif len(postData['first_name']) < 2:
            errors['first_name_length'] = "First name should be at least 2 characters"

        if not postData['last_name']:
            errors["missing_last_name"] = "Please Enter a Last name"
        elif len(postData['last_name']) < 2:
            errors['last_name_length'] = "Last name should be at least 2 characters"

        if not postData['email']:
            errors["missing_field_email"] = "Please Enter an email"
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email address"
        elif Users.objects.filter(email=postData['email']).exists():
            errors['email_exists'] = "Email already registered"

        password = postData.get('password')
        confirm_pw = postData.get('confirm_password')
        if not password or not confirm_pw:
            errors["missing_field_password"] = "Please enter password and confirm it"
        elif len(password) < 8:
            errors['password_length'] = "Password should be at least 8 characters"
        elif password != confirm_pw:
            errors['password_mismatch'] = "Password and Confirm Password do not match"

        if not postData.get('phone'):
            errors["missing_phone"] = "Please enter a phone number"
        elif not postData['phone'].isdigit():
            errors["invalid_phone"] = "Phone number should contain digits only"
        elif len(postData['phone']) != 11:  
            errors["phone_length"] = "Phone number should be 11 digits long"

        if not postData['address']:
            errors["missing_address"] = "Please Enter an address"
        elif len(postData['address']) < 2:
            errors['address_length'] = "Address should be at least 2 characters"

        return errors


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name


class Product(models.Model):
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    )

    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()  # أفضل من CharField للمرونة
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    stock_quantity = models.IntegerField()
    image = models.ImageField(upload_to='product_images/', default='product_images/default.png')
    is_featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return f"{self.name} ({self.price} EGP)"


class Users(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)  # لازم يتخزن Hashed
    role = models.CharField(max_length=45, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # تأكد إنه ما يتخزن plain text
        if not self.password.startswith('pbkdf2_'):  
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(Users, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cartitem'
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_cart_item')
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.user.email}"


class CustomerOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(Users, related_name='orders', on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_order'

    def __str__(self):
        return f"Order {self.order_id} - {self.user.email} - {self.status}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    order = models.ForeignKey(CustomerOrder, related_name='order_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"
