from django.contrib import admin
from .models import ColorTheme, Category, Product, Order

admin.site.register(ColorTheme)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)