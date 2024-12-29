from django.test import TestCase
from django.test import TestCase
from .models import User, Product, Oder, Oder_Iterm, Category, Developer, Publisher
# Create your tests here.

class RecommendSystemTestCase(TestCase):
    def setUp(self):
        """
        Thiết lập dữ liệu giả lập cho các đối tượng liên quan: User, Product, Oder, v.v.
        """
        # Tạo người dùng
        self.user = User.objects.create(username="testuser", email="testuser@example.com")

        # Tạo danh mục sản phẩm
        self.category1 = Category.objects.create(name="Action")
        self.category2 = Category.objects.create(name="Adventure")

        # Tạo nhà phát triển và nhà phát hành
        self.developer = Developer.objects.create(name="GameDev")
        self.publisher = Publisher.objects.create(name="GamePub")

        # Tạo sản phẩm
        self.product1 = Product.objects.create(
            name="Product1",
            price=50,
            developer=self.developer,
            publisher=self.publisher
        )
        self.product1.category.add(self.category1)

        self.product2 = Product.objects.create(
            name="Product2",
            price=70,
            developer=self.developer,
            publisher=self.publisher
        )
        self.product2.category.add(self.category2)

        self.product3 = Product.objects.create(
            name="Product3",
            price=90,
            developer=self.developer,
            publisher=self.publisher
        )
        self.product3.category.add(self.category1)

        self.product4 = Product.objects.create(
            name="Product4",
            price=60,
            developer=self.developer,
            publisher=self.publisher
        )
        self.product4.category.add(self.category2)

        # Tạo đơn hàng và mục đơn hàng
        self.order = Oder.objects.create(customer=self.user, price=120.0)

        Oder_Iterm.objects.create(
            product=self.product1,
            oder=self.order,
            quantity=2,
            price=self.product1.price
        )
        Oder_Iterm.objects.create(
            product=self.product2,
            oder=self.order,
            quantity=1,
            price=self.product2.price
        )

    def test_recommendSystem_with_data(self):
        """
        Test nếu phương thức `recommendSystem` trả về đúng sản phẩm gợi ý khi có dữ liệu mua hàng.
        """
        recommended_products = self.order.recommendSystem()

        # Kiểm tra nếu trả về đúng số lượng sản phẩm (giới hạn tối đa)
        self.assertLessEqual(len(recommended_products), 5)

        # Kiểm tra nếu sản phẩm gợi ý không trùng với sản phẩm đã mua
        purchased_products = Oder_Iterm.objects.filter(oder=self.order).values_list('product', flat=True)
        for product in recommended_products:
            self.assertNotIn(product.id, purchased_products)

    def test_recommendSystem_without_data(self):
        """
        Test nếu phương thức `recommendSystem` hoạt động khi không có dữ liệu mua hàng.
        """
        # Xóa tất cả đơn hàng
        Oder.objects.all().delete()

        # Thực hiện gọi phương thức gợi ý
        recommended_products = self.order.recommendSystem()

        # Kiểm tra nếu không có sản phẩm được gợi ý
        self.assertEqual(len(recommended_products), 0)