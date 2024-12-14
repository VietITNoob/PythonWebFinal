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
]

