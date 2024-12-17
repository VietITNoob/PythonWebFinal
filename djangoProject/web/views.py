from lib2to3.fixes.fix_input import context

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
        key = Product.objects.filter(name__icontains=searched)
    return render(request, '../templates/search.html', {'searched': searched, "key": key})


def productDetails(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Oder.objects.get_or_create(customer=customer,complete=False)
        items = order.oder_iterm_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_iterm':0, 'get_cart_total':0}
        cartItems = order['get_cart_iterm']
    Id = request.GET.get('id','')
    products = Product.objects.filter(id=Id)
    categories = Category.objects.filter(is_sub = False)
    context = {'product':products ,'categories':categories, 'items':items, 'order':order, 'cartItems':cartItems }
    return render(request, '../templates/ProductDetails.html',context)


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
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Lấy sản phẩm từ ID

    # Nếu giỏ hàng chưa tồn tại trong session, tạo mới một giỏ hàng là từ điển
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Lấy giỏ hàng từ session
    cart = request.session['cart']
    product_exists = False

    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1  # Tăng số lượng nếu sản phẩm đã có trong giỏ
        product_exists = True

    # Nếu sản phẩm chưa có, thêm sản phẩm mới vào giỏ hàng
    if not product_exists:
        cart[str(product.id)] = {
            'name': product.name,
            'price': product.price,
            'image_url': product.image.url,
            'quantity': 1
        }

    # Cập nhật giỏ hàng trong session
    request.session['cart'] = cart
    return redirect('view_cart')  # Chuyển hướng đến trang giỏ hàng


# Xóa sản phẩm khỏi giỏ hàng
def remove_from_cart(request, product_id):
    # Lấy giỏ hàng từ session
    cart = request.session.get('cart', {})

    # Nếu sản phẩm có trong giỏ hàng, xóa nó đi
    if str(product_id) in cart:
        del cart[str(product_id)]  # Xóa sản phẩm khỏi giỏ hàng

    # Cập nhật lại giỏ hàng vào session
    request.session['cart'] = cart

    return redirect('view_cart')  # Chuyển hướng đến trang giỏ hàng


def update_quantity(request, product_id, action):
    # Lấy giỏ hàng từ session
    cart = request.session.get('cart', {})

    # Chuyển product_id sang chuỗi để xử lý
    product_id = str(product_id)

    # Nếu sản phẩm tồn tại trong giỏ hàng
    if product_id in cart:
        if action == 'increase':
            cart[product_id]['quantity'] += 1  # Tăng số lượng
        elif action == 'decrease':
            if cart[product_id]['quantity'] > 1:
                cart[product_id]['quantity'] -= 1  # Giảm số lượng
            else:
                del cart[product_id]  # Xóa sản phẩm nếu số lượng = 0

    # Lưu giỏ hàng mới vào session
    request.session['cart'] = cart

    # Điều hướng quay lại trang giỏ hàng
    return redirect('view_cart')
