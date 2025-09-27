from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  

    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/<int:product_id>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete"),

    # Auth
    path('login/', views.login_register, name="login_register"),
    path('create_user/', views.create_user, name="create_user"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),

    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Users
    path("users/", views.user_list, name="user_list"),
    #path("users/<int:user_id>/edit/", views.user_edit, name="product_edit"),
    #path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
   
    # Orders
    path('orders/', views.order_list, name='order_list'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path("categories/<int:category_id>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="category_delete"),
    #cart
    
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path('cart/', views.view_cart, name='view_cart'),

    # Update
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/update-session/<int:product_id>/', views.update_cart_item_session, name='update_cart_item_session'),

    path('cart/delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/delete-session/<int:product_id>/', views.delete_cart_item_session, name='delete_cart_item_session'),

    path("checkout/", views.checkout, name="checkout"),


    path('all-products/', views.all_products, name='all_products'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


   
]