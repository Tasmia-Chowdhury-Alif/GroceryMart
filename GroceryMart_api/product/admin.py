from django.contrib import admin

from .models import Category, Brand, Product
from mptt.admin import MPTTModelAdmin

class CategoryModelAdmin(MPTTModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

# Register your models here.
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Brand)
admin.site.register(Product)