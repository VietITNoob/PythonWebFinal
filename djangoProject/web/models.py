from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm  
import pandas as pd
# Create your models here.

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categrory' ,null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null = True)
    slug = models.SlugField(max_length=200, null = True)
    def __str__(self):
        return self.name
class Publisher(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255, unique=True)  # Unique name for publisher
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')  # Status field

    def __str__(self):
        return self.name

class Developer(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255, unique=True)  # Unique name for developer
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')  # Status field

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=100, null = True)
    status = models.CharField(max_length=20, choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('coming_soon', 'Coming Soon')], null = True)
    price = models.FloatField()
    image = models.ImageField(upload_to = 'images/', null = True, blank = True)
    category = models.ManyToManyField(Category, related_name='products', blank=True)
    release_date = models.DateField(null=True, blank=True)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_all_categories(self):
        return ', '.join([category.name for category in self.category.all()])
    def get_category_name(self):
        return self.category.name

    def recommendSystem(self):
        # Lấy tất cả các sản phẩm trong c��ng danh mục với sản phẩm hiện tại
        recommended_products = Product.objects.filter(
            category__in=self.category.all()
        ).exclude(id=self.id).distinct()  # Exclude the current product

        # Randomly select a list of recommended products
        random_recommended_products = recommended_products.order_by('?')[:4]  # Get 4 random products

        return random_recommended_products
class Oder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)
    date_order = models.DateField(auto_now_add=True)
    complete = models.BooleanField(default=False , null = True , blank = False)
    transaction_id = models.CharField(max_length=100, null = True)

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_items(self):
        orderiterm = self.oder_iterm_set.all()
        total = sum([item.quantity for item in orderiterm])
        return total
    
    @property
    def get_cart_total(self):
        orderiterm = self.oder_iterm_set.all()
        total = sum([item.get_total for item in orderiterm])
        return total

    def recommendSystem(self):
        # Lấy tất cả các sản phẩm trong đơn hàng
        ordered_items = self.oder_iterm_set.all()
        product_ids = [item.product.id for item in ordered_items if item.product]

        # Tìm các sản phẩm khác trong cùng danh mục với các sản phẩm đã đặt
        recommended_products = Product.objects.filter(
            category__in=Product.objects.filter(id__in=product_ids).values_list('category', flat=True)
        ).exclude(id__in=product_ids).distinct()  # Exclude already purchased products

        # Randomly select a list of recommended products
        random_recommended_products = recommended_products.order_by('?')[:5]  # Get 5 random products

        return random_recommended_products

class Oder_Iterm(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null = True, blank = True)
    oder = models.ForeignKey(Oder, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=0, null = True, blank = True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

