from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login.html/', views.loginPage, name='login'),
    path('signup.html/', views.signup, name='signup'),
    path('logout.html/', views.logoutUser, name='logout'),
    path('search.html/', views.search, name='search'),
    path('productDetail.html/', views.productDetails, name='productDetail'),
    path('cart.html/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update_quantity/', views.update_quantity, name='update_quantity'),
]

