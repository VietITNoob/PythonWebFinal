from datetime import datetime
from itertools import product
from tkinter.constants import FALSE

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your models here.
class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categrory' ,null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null = True)
    slug = models.SlugField(max_length=200, null = True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, null = True)
    status = models.CharField(max_length=20, choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('coming_soon', 'Coming Soon')], null = True)
    price = models.FloatField()
    image = models.ImageField(upload_to = 'images/', null = True, blank = True)
    category = models.ManyToManyField(Category, related_name='products', blank=True)

    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_slug(self):
        slugs = [cat.slug for cat in self.category.all()]  # Lấy slug của tất cả các danh mục
        return ''.join(f'<li>{slug}</li>' for slug in slugs)   # Trả về danh sách các slug
class Oder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)
    date_order = models.DateField(auto_now_add=True)
    complete = models.BooleanField(default=False , null = True , blank = False)
    transaction_id = models.CharField(max_length=100, null = True)

    def __str__(self):
        return str(self.id)

class Oder_Iterm(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null = True, blank = True)
    oder = models.ForeignKey(Oder, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=0, null = True, blank = True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
