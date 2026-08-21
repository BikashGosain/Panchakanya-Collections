# Create your tests here.
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Rings")

    def test_product_slug_auto_generated(self):
        product = Product.objects.create(
            name="Gold Ring",
            sku="SKU001",
            category=self.category,
            metal_type="gold",
            price=50000,
        )
        self.assertEqual(product.slug, "gold-ring")

    def test_duplicate_name_gets_unique_slug(self):
        Product.objects.create(
            name="Gold Ring",
            sku="SKU001",
            category=self.category,
            metal_type="gold",
            price=50000,
        )
        second = Product.objects.create(
            name="Gold Ring",
            sku="SKU002",
            category=self.category,
            metal_type="gold",
            price=55000,
        )
        self.assertEqual(second.slug, "gold-ring-1")

    def test_only_one_cover_image_per_product(self):
        from .models import ProductImage

        product = Product.objects.create(
            name="Silver Chain",
            sku="SKU003",
            category=self.category,
            metal_type="silver",
            price=8000,
        )
        img1 = ProductImage.objects.create(product=product, is_primary=True)
        img2 = ProductImage.objects.create(product=product, is_primary=True)

        img1.refresh_from_db()
        img2.refresh_from_db()
        self.assertFalse(img1.is_primary)
        self.assertTrue(img2.is_primary)

    def test_soft_deleted_product_excluded_from_default_queryset(self):
        from .models import Product

        product = Product.objects.create(
            name="Silver Bangle",
            sku="SKU010",
            category=self.category,
            metal_type="silver",
            price=12000,
        )
        product.soft_delete()

        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(Product.all_objects.filter(pk=product.pk).exists())

    def test_restored_product_reappears_in_default_queryset(self):
        from .models import Product

        product = Product.objects.create(
            name="Rose Gold Bracelet",
            sku="SKU011",
            category=self.category,
            metal_type="gold",
            price=30000,
        )
        product.soft_delete()
        product.restore()

        self.assertTrue(Product.objects.filter(pk=product.pk).exists())
        self.assertIsNone(product.deleted_at)


class ProductViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Rings")
        self.product = Product.objects.create(
            name="Gold Ring",
            sku="SKU001",
            category=self.category,
            metal_type="gold",
            price=50000,
            status="active",
        )

    def test_product_list_shows_active_products(self):
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, "Gold Ring")

    def test_inactive_product_hidden_from_list(self):
        self.product.status = "inactive"
        self.product.save()
        response = self.client.get(reverse("products:list"))
        self.assertNotContains(response, "Gold Ring")

    def test_product_detail_page_loads(self):
        response = self.client.get(reverse("products:detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gold Ring")

    def test_category_filter(self):
        other_category = Category.objects.create(name="Necklaces")
        Product.objects.create(
            name="Diamond Necklace",
            sku="SKU004",
            category=other_category,
            metal_type="diamond",
            price=90000,
            status="active",
        )
        response = self.client.get(reverse("products:list"), {"category": "rings"})
        self.assertContains(response, "Gold Ring")
        self.assertNotContains(response, "Diamond Necklace")

    def test_soft_deleted_product_hidden_from_shop_list(self):
        self.product.soft_delete()
        response = self.client.get(reverse("products:list"))
        self.assertNotContains(response, "Gold Ring")
