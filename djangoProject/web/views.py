
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def home(request):
    products =  Prodcut.objects.all()
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
        else: messages.info(request, 'Invalid username or password !')
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
    return render(request, '../templates/signup.html',context)
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        key = Prodcut.objects.filter(name__icontains=searched)
    return render(request, '../templates/search.html', {'searched': searched, "key": key})

def productDetails(request):
    return render(request, '../templates/ProductDetails.html')


