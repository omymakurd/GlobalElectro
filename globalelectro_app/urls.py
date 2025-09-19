from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('products/', views.product_list, name='product_list'),  
    path('login/', views.login_register, name="login_register"),
    path('create_user',views.create_user,name="create_user"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_add/', views.user_add, name='user_add'),  
    path('categories/', views.category_list, name='category_list'),
    path('orders/', views.order_list, name='order_list'),
    path('users/', views.user_list, name='user_list'),

]