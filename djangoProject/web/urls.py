from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('search/', views.search, name='search'),
    path('productDetail/', views.productDetails, name='productDetail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update_item/', views.updateItem, name='updateItem'),
]

