from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def home(request):
    """
    Home View: Displays main products and recommended products based on order history.
    """
    categories = Category.objects.filter(is_sub=False)
    products = Product.objects.all()

    # Check if the user is authenticated for recommendations
    if request.user.is_authenticated:
        current_order = Oder.objects.filter(customer=request.user).last()

        # Handle recommendation only if an order exists
        if current_order:
            try:
                recommended_products = current_order.recommendSystem()
            except Exception as e:
                print("Error in recommendation system:", e)
                recommended_products = []
        else:
            recommended_products = []
    else:
        recommended_products = []

    context = {
        'products': products,
        'recommended_products': recommended_products,
        'categories': categories
    }

    return render(request, 'index.html', context)
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
    categories = Category.objects.filter(is_sub=False)
    context = {'categories': categories}
    return render(request, '../templates/login.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, 'You have been logged out !')
    return redirect('home')


# đăng kí
def signup(request):
    categories = Category.objects.filter(is_sub=False)
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form': form, 'categories': categories}
    return render(request, '../templates/signup.html', context)


def search(request):
    categories = Category.objects.filter(is_sub=False)
    if request.method == 'POST':
        searched = request.POST['searched']
        key = Product.objects.filter(name__icontains=searched)
    return render(request, '../templates/search.html', {'searched': searched, "key": key, "categories": categories})


def productDetails(request):
    """
    View to display product details and recommendations based on the current product.
    """
    if request.user.is_authenticated:
        customer = request.user
        orders = Oder.objects.filter(customer=customer)

        # Get items and prepare the order summary
        if orders.exists():
            order = orders.first()  # Retrieve the first order if multiple exist
            items = order.oder_iterm_set.all()
        else:
            items = []
            order = {'get_cart_iterm': 0, 'get_cart_total': 0}
    else:
        items = []
        order = {'get_cart_iterm': 0, 'get_cart_total': 0}

    # Fetch product details based on ID from GET parameters
    product_id = request.GET.get('id', '')
    products = Product.objects.filter(id=product_id)
    categories = Category.objects.filter(is_sub=False)
    current_product = products.first() if products.exists() else None
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=current_product).exists() # kiểm tra xem có trong wishlist của người dùng chưa

    # Fetch recommendations for the current product
    if current_product:
        try:
            recommended_products = current_product.recommendSystem()
        except Exception as e:
            print("Error in product recommendation:", e)
            recommended_products = []
    else:
        recommended_products = []

    context = {
        'products': products,
        'categories': categories,
        'items': items,
        'order': order,
        'recommended_products': recommended_products,
        'is_in_wishlist': is_in_wishlist
    }

    return render(request, '../templates/ProductDetails.html', context)


# chức năng thêm vào giỏ hàng
def view_cart(request):
    # Lấy giỏ hàng từ session, mặc định là dictionary rỗng nếu không có
    cart_items = request.session.get('cart', {})
    categories = Category.objects.filter(is_sub=False)
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

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price,'categories': categories})


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
            price=sum(item['price'] * item['quantity'] for item in cart_items.values()),
        )

        # Thêm các OrderItem
        for product_id, item in cart_items.items():
            product = Product.objects.get(id=product_id)
            Oder_Iterm.objects.create(
                product=product,
                oder=oder,
                quantity=item['quantity'],
                price=product.price, # giá tại thời điểm mua hàng
            )
            # product.sales += item['quantity'] # tăng số lượng bán của sản phẩm lên 
            product.update_sales()
       
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

def user_information(request):
     # Kiểm tra nếu người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect('login')  # chuyển hướng đến trang đăng nhập
    categories = Category.objects.filter(is_sub=False)
    context = {'categories': categories}
    return render(request,'../templates/user_information.html', context)

def user_history(request):
     # Kiểm tra nếu người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect('login')  # chuyển hướng đến trang đăng nhập
    categories = Category.objects.filter(is_sub=False)
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
                'price': item.price,                       # Giá của sản phẩm
                'total': item.quantity * item.price,       # Tổng giá cho từng sản phẩm
                'date_added': item.date_added              # Ngày mua sản phẩm
            })
        
        order_items_data.append({
            'order_id': order.id,                        # ID đơn hàng
            'order_date': order.date_order,              # Ngày đặt hàng
            'items': items_data                           # Danh sách sản phẩm trong đơn hàng
        })
    
    # Truyền dữ liệu vào template
    return render(request, 'user_history.html', {'order_items_data': order_items_data,'categories': categories})


def user_wishlist(request):
    # Kiểm tra nếu người dùng chưa đăng nhập
    if not request.user.is_authenticated:
        return redirect('login')  # chuyển hướng đến trang đăng nhập

    # Lấy tất cả danh mục không phải subcategories
    categories = Category.objects.filter(is_sub=False)

    # Lấy danh sách wishlist của người dùng đã đăng nhập
    list_wish = Wishlist.objects.filter(user=request.user)

    # Lấy tất cả các sản phẩm trong wishlist để giảm số lượng truy vấn
    products_in_wishlist = Product.objects.filter(id__in=[game.product.id for game in list_wish])

    # Chuẩn bị dữ liệu để gửi đến template
    data_wish_list_view = []
    for game in list_wish:
        product = products_in_wishlist.get(id=game.product.id)  # Lấy sản phẩm từ danh sách đã lấy trước đó
        data_wish_list_view.append({
            'product_image': product.image,    # Hình ảnh sản phẩm
            'product_name': product.name,      # Tên sản phẩm
            'price': product.price,            # Giá của sản phẩm
            'date_added': game.date_added,      # Ngày thêm vào wishlist
            'product_id': product.id,          # Thêm ID sản phẩm vào context
        })

    # Truyền dữ liệu vào context
    context = {'categories': categories, 'data_wish_list_view': data_wish_list_view}
    return render(request, 'user_wishlist.html', context)

def checkout(request):
    return render(request,'../templates/checkout.html')

def ViewAll(request):
    categories = Category.objects.filter(is_sub=False)
    products = Product.objects.all()
    context = {'products': products,'categories': categories}
    return render(request,'../templates/ViewAll.html',context)
def category(request) :
    categories = Category.objects.filter(is_sub = False)
    active_category = request.GET.get('category','')
    if active_category:
        products = Product.objects.filter(category__slug = active_category)
    context = {'products': products,'categories':categories}
    return render(request,'categories.html',context)

def add_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Nếu người dùng chưa đăng nhập, chuyển hướng đến trang đăng nhập
    
    product = Product.objects.get(id=product_id)  # Lấy sản phẩm theo ID
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.name} added your wish list.")
    # else:
    #     messages.info(request, f"{product.name} is ex.") 

    # Chuyển hướng về trang trước đó (hoặc chuyển về trang home nếu không có referrer)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def remove_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Nếu người dùng chưa đăng nhập, chuyển hướng đến trang đăng nhập
    
    product = Product.objects.get(id=product_id)  # Lấy sản phẩm theo ID
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed your wish list!")
    # else:
    #     messages.info(request, f"{product.name} không có trong danh sách yêu thích của bạn.")

    # Chuyển hướng về trang trước đó (hoặc chuyển về trang home nếu không có referrer)
    return redirect(request.META.get('HTTP_REFERER', 'home'))