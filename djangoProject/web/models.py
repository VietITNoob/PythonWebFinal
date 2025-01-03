from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm  
import pandas as pd
from django.db.models import Sum
from mlxtend.frequent_patterns import apriori, association_rules
# Create your models here.

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categrory' ,null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null = True)
    slug = models.SlugField(max_length=200, null = True)
    def __str__(self):
        return self.name
class Publisher(models.Model):
    id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=255, unique=True) 
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')  # Status field

    def __str__(self):
        return self.name

class Developer(models.Model):
    id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=255, unique=True)  
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
    sales = models.PositiveIntegerField(default=0) 
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
    
    @property
    def sale_num(self):
        num = Oder_Iterm.objects.filter(product=self).aggregate(total=models.Sum('quantity')).get('total', 0)
        return num

    # Phương thức cập nhật số lượng bán
    def update_sales(self):
        self.sales = self.sale_num 
        self.save()

    def recommendSystem(self):
        categories = self.category.all()
        recommended_products = Product.objects.filter(category__in=categories).exclude(id=self.id).distinct().order_by('-sales')[:5]

        return recommended_products


class Oder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)
    date_order = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        return str(self.id)
    
    # @property
    # def get_cart_items(self):
    #     orderiterm = self.oder_iterm_set.all()
    #     total = sum([item.quantity for item in orderiterm])
    #     return total
    
    # @property
    # def get_cart_total(self):
    #     orderiterm = self.oder_iterm_set.all()
    #     total = sum([item.get_total for item in orderiterm])
    #     return total

    def recommendSystem(self):
        """
        Gợi ý sản phẩm dựa trên luật kết hợp và các sản phẩm có số lượng bán lớn.
        """
        try:
            # --- Bước 1: Lấy dữ liệu chi tiêu của người dùng ---
            all_orders = Oder.objects.filter(customer=self.customer)  # Tất cả đơn hàng của khách
            order_items = Oder_Iterm.objects.filter(oder__in=all_orders).select_related('product')  # Các mục đơn hàng

            # Chuẩn bị dữ liệu gợi ý
            data = []
            for item in order_items:
                product_categories = item.product.category.all()  # Lấy danh mục của sản phẩm
                for category in product_categories:
                    data.append({
                        'order_id': item.oder.id,
                        'category': category.name,
                        'amount_spent': float(item.quantity) * float(item.price)
                    })

            # Chuyển đổi sang DataFrame
            df = pd.DataFrame(data)
            if df.empty:
                return Product.objects.none()  # Nếu không có dữ liệu, trả về rỗng

            # --- Bước 2: Chuẩn bị bảng Pivot ---
            df['amount_spent_bin'] = pd.qcut(df['amount_spent'], q=4, labels=['Thấp', 'Trung bình', 'Cao', 'Rất cao'])
            pivot_table = df.pivot_table(index='order_id', columns='category', aggfunc='size', fill_value=0).astype(
                bool)

            # --- Bước 3: Áp dụng thuật toán Apriori ---
            frequent_itemsets = apriori(pivot_table, min_support=0.1, use_colnames=True)
            if frequent_itemsets.empty:
                return Product.objects.none()

            # Tính số lượng tập phổ biến
            frequent_itemsets['support_count'] = frequent_itemsets['support'] * len(pivot_table)
            num_itemsets = len(frequent_itemsets)

            # --- Bước 4: Tạo luật kết hợp ---
            rules = association_rules(
                frequent_itemsets,
                metric='lift',
                min_threshold=1.0,
                num_itemsets=num_itemsets
            )
            recommended_categories = set()
            for _, row in rules.iterrows():
                for consequent in row['consequents']:
                    if consequent not in recommended_categories:
                        recommended_categories.add(consequent)

            # --- Bước 5: Thống kê sản phẩm bán chạy ---
            best_selling_products = Oder_Iterm.objects.values('product').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')

            # Lấy danh sách các sản phẩm gợi ý từ luật kết hợp
            recommended_products_from_rules = Product.objects.filter(
                category__name__in=recommended_categories
            ).exclude(
                id__in=[item.product.id for item in order_items]  # Loại các sản phẩm đã mua
            ).distinct()

            # Lọc các sản phẩm bán chạy nhưng chưa được mua
            best_selling_ids = [item['product'] for item in best_selling_products]
            recommended_products_from_sales = Product.objects.filter(
                id__in=best_selling_ids
            ).exclude(
                id__in=[item.product.id for item in order_items]
            ).distinct()

            # Kết hợp các sản phẩm gợi ý: Ưu tiên sản phẩm từ luật kết hợp trước
            final_recommendations = list(recommended_products_from_rules) + list(recommended_products_from_sales)
            final_recommendations = list(dict.fromkeys(final_recommendations))  # Bỏ trùng lặp

            # Giới hạn số lượng gợi ý
            return final_recommendations[:5]

        except Exception as e:
            print(f"Lỗi trong hệ thống gợi ý: {e}")
            return Product.objects.none()

class Oder_Iterm(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null = True, blank = True)
    oder = models.ForeignKey(Oder, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=0, null = True, blank = True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    # @property
    # def get_total(self):
    #     total = self.product.price * self.quantity
    #     return total

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")  # Người dùng
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")  # Sản phẩm (game)
    date_added = models.DateField(auto_now_add=True)  # Ngày thêm vào danh sách yêu thích

    class Meta:
        unique_together = ('user', 'product')  # Đảm bảo mỗi người chỉ có thể thêm một game một lần vào wishlist

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
