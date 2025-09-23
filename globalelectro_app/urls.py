from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path("products/", views.product_list, name="product_list"),
    path("products/<int:product_id>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete"),

    path('login/', views.login_register, name="login_register"),
    path('create_user',views.create_user,name="create_user"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_add/', views.user_add, name='user_add'),  
    path('orders/', views.order_list, name='order_list'),
    path('users/', views.user_list, name='user_list'),
    path('categories/', views.category_list, name='category_list'),
    path("categories/<int:category_id>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="category_delete"),
    


]