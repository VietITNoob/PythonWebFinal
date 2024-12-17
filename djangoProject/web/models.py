from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from mlxtend.frequent_patterns import apriori,association_rules
import pandas as pd
# Create your models here.
class Publisher(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255, unique=True)  # Unique name for the publisher
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')  # Status field

class Developer(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255, unique=True)  # Unique name for the developer
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')  # Status field
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
    release_date = models.DateField(null=True, blank=True)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)

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

    def get_recommendations(self):
        
        # Lấy tất cả các đơn hàng
        orders = Oder.objects.all()
        
        # Tạo DataFrame từ các đơn hàng
        order_data = []
        for order in orders:
            items = order.oder_iterm_set.all()
            order_data.append([item.product.id for item in items])
        
        # Chuyển đổi dữ liệu thành DataFrame
        df = pd.DataFrame(order_data)
        
        # Tính toán các quy tắc kết hợp
        frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
        
        # Lấy các sản phẩm liên quan đến sản phẩm hiện tại
        related_products = rules[rules['antecedents'].apply(lambda x: self.id in x)]
        
        # Trả về danh sách các sản phẩm gợi ý
        return [Product.objects.get(id=product_id) for product_id in related_products['consequents']]

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

