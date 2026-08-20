from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    show_on_home = models.BooleanField(default=False, verbose_name="Show on homepage")

    class Meta:
        verbose_name_plural = "categories"

        constraints = [
            models.UniqueConstraint(
                fields=["name", "parent"],
                name="unique_category_name_per_parent",
            ),
        ]

    @property
    def has_children(self):
        return self.subcategories.exists()

    def clean(self):
        """
        Prevent invalid category relationships.
        """

        super().clean()

        # A category cannot be its own parent.
        if self.parent_id == self.pk:
            raise ValidationError({"parent": "A category cannot be its own parent."})

        # Prevent circular relationships.
        ancestor = self.parent

        while ancestor is not None:
            if ancestor.pk == self.pk:
                raise ValidationError(
                    {
                        "parent": (
                            "Invalid parent. This would create "
                            "a circular category structure."
                        )
                    }
                )

            ancestor = ancestor.parent

    def save(self, *args, **kwargs):

        self.full_clean()

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    METAL_CHOICES = [
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("diamond", "Diamond"),
        ("platinum", "Platinum"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    metal_type = models.CharField(max_length=20, choices=METAL_CHOICES)
    purity = models.CharField(max_length=20, blank=True, help_text="e.g. 18K, 22K, 24K")
    weight_grams = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False, verbose_name="Cover image")

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} image"
