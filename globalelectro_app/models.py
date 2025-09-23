from django.db import models
import re
from datetime import date

class userManager(models.Manager):
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
            errors["missing_address"] = "Please Enter a address"
        elif len(postData['address']) < 2:
            errors['address_length'] = "address should be at least 2 characters"


        return errors

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        #managed = False
        db_table = 'category'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=45)
    stock_quantity = models.IntegerField()
    image = models.ImageField(upload_to='product_images/')
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       # managed = False
        db_table = 'product'

class Users(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
     
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email=models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=45,choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=45)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects=userManager()
    class Meta:
       # managed = False
        db_table = 'users'

class Cartitem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    user = models.ForeignKey(Users, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       
        db_table = 'cartitem'

class CustomerOrder(models.Model):
    order_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=45)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Users, related_name='orders', on_delete=models.CASCADE)

    class Meta:
       
        db_table = 'customer_order'

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    order = models.ForeignKey(CustomerOrder, related_name='order_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        
        db_table = 'order_item'
