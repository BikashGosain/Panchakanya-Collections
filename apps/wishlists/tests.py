from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.products.models import Category, Product

from .models import Wishlist


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            phone_number="9812345678",
            address="Test Address",
            city="Kathmandu",
        )

        self.category = Category.objects.create(
            name="Rings",
        )

        self.product = Product.objects.create(
            name="Test Ring",
            sku="TEST-RING-001",
            category=self.category,
            metal_type="gold",
            price=45000,
            stock=10,
        )

    def test_wishlist_creation(self):
        wishlist = Wishlist.objects.create(
            user=self.user,
            product=self.product,
        )

        self.assertEqual(wishlist.user, self.user)
        self.assertEqual(wishlist.product, self.product)

    def test_duplicate_wishlist_is_not_allowed(self):
        Wishlist.objects.create(
            user=self.user,
            product=self.product,
        )

        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(
                user=self.user,
                product=self.product,
            )


class WishlistViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="viewtest",
            email="viewtest@example.com",
            password="testpassword",
            phone_number="9812345679",
            address="Test Address",
            city="Kathmandu",
        )

        self.category = Category.objects.create(
            name="Necklaces",
        )

        self.product = Product.objects.create(
            name="Test Necklace",
            sku="TEST-NECKLACE-001",
            category=self.category,
            metal_type="gold",
            price=50000,
            stock=5,
        )

    def test_add_to_wishlist(self):
        self.client.login(
            username="viewtest",
            password="testpassword",
        )

        response = self.client.post(
            reverse(
                "wishlists:add",
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

        self.assertTrue(
            Wishlist.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    def test_remove_from_wishlist(self):
        self.client.login(
            username="viewtest",
            password="testpassword",
        )

        Wishlist.objects.create(
            user=self.user,
            product=self.product,
        )

        response = self.client.post(
            reverse(
                "wishlists:remove",
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

        self.assertFalse(
            Wishlist.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )
