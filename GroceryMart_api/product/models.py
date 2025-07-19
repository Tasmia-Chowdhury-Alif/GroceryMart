from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits= 10, decimal_places= 2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = TreeForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_digital = models.BooleanField(default=False) # digital means does it requires delevery 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
