from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, '../templates/index.html', context)
def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Invalid username or password !')
        return redirect('login')

    return render(request, '../templates/login.html', {})


def logoutUser(request):
    logout(request)
    messages.success(request, 'You have been logged out !')
    return redirect('home')


# đăng kí
def signup(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, '../templates/signup.html', context)


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        key = Prodcut.objects.filter(name__icontains=searched)
    return render(request, '../templates/search.html', {'searched': searched, "key": key})


def productDetails(request):
    return render(request, '../templates/ProductDetails.html')


# chức năng thêm vào giỏ hàng
def view_cart(request):
    # Lấy giỏ hàng từ session, mặc định là dictionary rỗng nếu không có
    cart_items = request.session.get('cart', {})

    # Kiểm tra và đảm bảo cart_items không rỗng, nếu rỗng thì trả về thông báo thích hợp
    if not cart_items:
        return render(request, 'cart.html',
                      {'cart_items': cart_items, 'total_price': 0, 'message': 'Giỏ hàng của bạn chưa có sản phẩm!'})

    # Kiểm tra và tính toán tổng giá trị cho mỗi sản phẩm trong giỏ hàng
    total_price = 0
    for product_id, item in cart_items.items():
        if isinstance(item, dict) and 'price' in item and 'quantity' in item:
            item['total'] = item['price'] * item['quantity']
            total_price += item['total']
        else:
            print(f"Lỗi trong dữ liệu sản phẩm: {item}")  # Logging thông tin sản phẩm có lỗi

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


# Thêm một sản phẩm vào giỏ hàng


# Xóa sản phẩm khỏi giỏ hàng

