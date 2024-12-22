from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
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
        # Sử dụng filter để lấy tất cả đơn hàng phù hợp
        orders = Oder.objects.filter(customer=customer, complete=False)
        
        if orders.exists():
            order = orders.first()  # Lấy đơn hàng đầu tiên nếu có nhiều đơn hàng
            items = order.oder_iterm_set.all()
            cartItems = order.get_cart_items
        else:
            items = []
            order = {'get_cart_iterm': 0, 'get_cart_total': 0}
            cartItems = order['get_cart_iterm']
    else:
        items = []
        order = {'get_cart_iterm': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_iterm']
    
    Id = request.GET.get('id', '')
    products = Product.objects.filter(id=Id)
    categories = Category.objects.filter(is_sub=False)
    context = {'products': products, 'categories': categories, 'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, '../templates/ProductDetails.html', context)


# # chức năng thêm vào giỏ hàng
# def view_cart(request):
#     if request.user.is_authenticated:
#         customer = request.user
#         order, created = Oder.objects.get_or_create(customer=customer, complete=False)
#         items = order.oder_iterm_set.all()
#     else:
#         items = []
#         order = {'get_cart_iterm': 0, 'get_cart_total': 0}
#     context = {'items': items, 'order': order}
#     return render(request, '../templates/cart.html', context)
# def updateItem(request):
#     data = json.loads(request.body)
#     productId = data['productId']
#     action = data['action']
#     customer = request.user
#     product = Product.objects.get(id=productId)
#     order, created = Oder.objects.get_or_create(customer=customer, complete=False)
#     orderItem, created = Oder_Iterm.objects.get_or_create(oder=order, product=product)

#     if action == 'add':
#         orderItem.quantity += 1
#     elif action == 'remove':
#         orderItem.quantity -= 1
    
#     orderItem.save()
    
#     if orderItem.quantity <= 0:
#         orderItem.delete()
    
#     return JsonResponse('added', safe=False)


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
    if not request.user.is_authenticated: # đăng nhập để thêm game vào giỏ hàng
        return redirect('login')  # chuyển hướng đến trang đăng nhập
    
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
    
    # Thêm thông báo thành công
    messages.success(request, f'Added {product.name} to cart!')  # Thông báo sản phẩm đã được thêm vào giỏ hàng

    return JsonResponse({'message': f'Added {product.name} to cart!'}, status=200)  # Trả về thông báo thành công


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


def update_quantity(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        # if not product_id or not action:
        #     messages.error(request, "Invalid data.")
        #     return redirect('view_cart')

        cart = request.session.get('cart', {})
        product_id = str(product_id)

        if product_id in cart:
            if action == 'increase':
                cart[product_id]['quantity'] += 1
            elif action == 'decrease':
                if cart[product_id]['quantity'] > 1:
                    cart[product_id]['quantity'] -= 1
                else:
                    del cart[product_id]

        request.session['cart'] = cart
        return redirect('view_cart')

    return HttpResponseBadRequest("Invalid request method.")



def buy(request):
    # Kiểm tra nếu người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect('login')  # chuyển hướng đến trang đăng nhập

    cart_items = request.session.get('cart', {})

    if cart_items:  # Nếu giỏ hàng không trống
        # Tạo oder mới
        oder = Oder.objects.create(
            customer=request.user,
            
            # price=sum(item['price'] * item['quantity'] for item in cart_items.values()),
        )

        # Thêm các OrderItem
        for product_id, item in cart_items.items():
            product = Product.objects.get(id=product_id)
            Oder_Iterm.objects.create(
                product=product,
                oder=oder,
                quantity=item['quantity'],
            )
        # Xóa giỏ hàng sau khi xử lý thành công
        del request.session['cart']

        # return render(request, 'cart/checkout_success.html', {'order': order}) 
        messages.success(request, "Purchase successful!")
        return redirect('home') 
    else:
        messages.error(request, "Your shopping cart don't have any product!")
        return redirect('view_cart') 


def user_share_temp(request):
    return render(request,'../templates/user_share_temp.html')

# @login_required (chưa làm xong nên chưa thêm để dễ vô)
def user_information(request):
    return render(request,'../templates/user_information.html')


# def user_history(request):
#     return render(request,'../templates/user_history.html')

# @login_required  
# def user_history(request):
#     # Get all orders for the logged-in user
#     orders = Oder.objects.filter(customer=request.user)

#     # Prepare the order items data for each order
#     order_items_data = []
#     for order in orders:
#         order_items = Oder_Iterm.objects.filter(oder=order)
#         order_items_data.append({
#             'order': order,
#             'order_items': order_items
#         })
    
#     # Pass the data to the template
#     return render(request, '../templates/user_history.html', {'order_items_data': order_items_data})
def user_history(request):
    # Lấy tất cả đơn hàng của người dùng đã đăng nhập
    orders = Oder.objects.filter(customer=request.user)

    # Chuẩn bị dữ liệu cho mỗi đơn hàng
    order_items_data = []
    for order in orders:
        order_items = Oder_Iterm.objects.filter(oder=order)
        
        # Tạo danh sách các mục trong đơn hàng với thông tin chi tiết như hình ảnh game, tên, số lượng, giá, tổng tiền, và ngày mua
        items_data = []
        for item in order_items:
            items_data.append({
                'product_image': item.product.ImageURL,    # Hình ảnh game
                'product_name': item.product.name,         # Tên game
                'quantity': item.quantity,                 # Số lượng
                'price': item.product.price,               # Giá của sản ph���m
                'total': item.get_total,                   # Tổng giá cho từng sản phẩm
                'date_added': item.date_added              # Ngày mua sản phẩm
            })
        
        order_items_data.append({
            'order_id': order.id,                        # ID đơn hàng
            'order_date': order.date_order,              # Ngày đặt hàng
            'items': items_data                           # Danh sách sản phẩm trong đơn hàng
        })
    
    # Truyền dữ liệu vào template
    return render(request, 'user_history.html', {'order_items_data': order_items_data})


def user_wishlist(request):
    return render(request,'../templates/user_wishlist.html')

def checkout(request):
    return render(request,'../templates/checkout.html')

def ViewAll(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request,'../templates/ViewAll.html',context)