from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.products.models import Category, Product

from .models import Cart, CartItem


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        self.category = Category.objects.create(
            name="Rings",
        )

        self.product = Product.objects.create(
            name="Test Gold Ring",
            sku="TEST-RING-001",
            category=self.category,
            metal_type="gold",
            price=45000,
            stock=10,
            status="active",
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user)

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_duplicate_product_not_allowed_in_cart(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )

        with self.assertRaises(IntegrityError):
            CartItem.objects.create(
                cart=cart,
                product=self.product,
                quantity=2,
            )

    def test_cart_total_price(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )

        self.assertEqual(cart.total_price, 90000)


class CartViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        self.category = Category.objects.create(
            name="Rings",
        )

        self.product = Product.objects.create(
            name="Test Gold Ring",
            sku="TEST-RING-001",
            category=self.category,
            metal_type="gold",
            price=45000,
            stock=10,
            status="active",
        )

        self.client.login(
            username="testuser",
            password="testpassword",
        )

    def test_add_to_cart(self):
        response = self.client.post(
            reverse(
                "cart:add",
                args=[self.product.id],
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "products:detail",
                kwargs={"slug": self.product.slug},
            ),
        )

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(
            cart=cart,
            product=self.product,
        )

        self.assertEqual(item.quantity, 1)

    def test_add_same_product_increases_quantity(self):
        self.client.post(
            reverse(
                "cart:add",
                args=[self.product.id],
            )
        )

        self.client.post(
            reverse(
                "cart:add",
                args=[self.product.id],
            )
        )

        cart = Cart.objects.get(user=self.user)

        self.assertEqual(
            cart.items.count(),
            1,
        )

        item = cart.items.get(
            product=self.product,
        )

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_remove_from_cart(self):
        cart = Cart.objects.create(
            user=self.user,
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            reverse(
                "cart:remove",
                args=[self.product.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("cart:view"),
        )

        self.assertFalse(
            CartItem.objects.filter(
                cart=cart,
                product=self.product,
            ).exists()
        )

    def test_update_cart_quantity(self):
        cart = Cart.objects.create(
            user=self.user,
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            reverse(
                "cart:update",
                args=[self.product.id],
            ),
            {"quantity": 5},
        )

        self.assertRedirects(
            response,
            reverse("cart:view"),
        )

        item = CartItem.objects.get(
            cart=cart,
            product=self.product,
        )

        self.assertEqual(
            item.quantity,
            5,
        )

    def test_cart_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("cart:view"),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f"{reverse('accounts:login')}?next={reverse('cart:view')}",
        )
