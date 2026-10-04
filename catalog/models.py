from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon_name = models.CharField(max_length=50, blank=True, default='sun', help_text='Icon identifier (e.g. sun, zap, battery, tool, droplet)')
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    product_code = models.CharField(max_length=60, unique=True, help_text='SKU or Product Code')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True, default='')
    technology_type = models.CharField(max_length=100, blank=True, default='', help_text='e.g. Mono PERC, Bifacial TopCon, LiFePO4, 3-Phase Hybrid')
    power_watts = models.PositiveIntegerField(null=True, blank=True, help_text='Nominal power output in Watts (e.g. 550, 10000 for 10kW)')
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    is_featured = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='products/', blank=True, null=True)
    datasheet_pdf = models.FileField(upload_to='products/datasheets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.name}-{self.product_code}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.product_code})"

    @property
    def display_power(self):
        if not self.power_watts:
            return None
        if self.power_watts >= 1000:
            kw = self.power_watts / 1000
            return f"{kw:.1f} kW" if kw % 1 != 0 else f"{int(kw)} kW"
        return f"{self.power_watts} W"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=150, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.product.name}"


class SpecificationAttribute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=30, blank=True, default='', help_text='e.g., W, kW, V, %, kg, Years')
    description = models.CharField(max_length=250, blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})" if self.unit else self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    attribute = models.ForeignKey(SpecificationAttribute, on_delete=models.CASCADE, related_name='product_specs')
    value = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('product', 'attribute')

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"
