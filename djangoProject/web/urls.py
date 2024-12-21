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
    # path('update_item/', views.updateItem, name='updateItem'),

    #chức năng thêm, xóa, sửa, mua sản phầm
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update_quantity/', views.update_quantity, name='update_quantity'),
    path('cart/buy/', views.buy, name='buy'),

    # dẫn tới temp mẫu user
    path('user_share_temp/', views.user_share_temp, name='user_share_temp'),

    # thông tin, lịch sử mua hàng, danh sách yêu thích
    path('user_information/', views.user_information, name='user_information'),
    path('user_history/', views.user_history, name='user_history'),
    path('user_wishlist/', views.user_wishlist, name='user_wishlist'),
    path('checkout/', views.checkout, name='checkout'),

]

