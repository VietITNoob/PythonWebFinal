from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from mlxtend.frequent_patterns import apriori,association_rules
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

