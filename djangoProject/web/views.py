from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
    if request.user.is_authenticated:
        customer = request.user
        order, created = Oder.objects.get_or_create(customer=customer, complete=False)
        items = order.oder_iterm_set.all()
    else:
        items = []
        order = {'get_cart_iterm': 0, 'get_cart_total': 0}
    context = {'items': items, 'order': order}
    return render(request, '../templates/cart.html', context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Oder.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = Oder_Iterm.objects.get_or_create(oder=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('added', safe=False)