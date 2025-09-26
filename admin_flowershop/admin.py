from django.contrib import admin
from .models import ColorTheme, Category, Product, Order


@admin.register(ColorTheme)
class ColorThemeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'categories_names', 'price', 'available', 'color_themes_names']
    list_filter = ['categories', 'color_themes', 'available']
    list_editable = ['price', 'available']
    search_fields = ['name']

    def categories_names(self, obj):
        return ", ".join([c.name for c in obj.categories.all()]) if obj.categories.exists() else "—"
    categories_names.short_description = "Категории"

    def color_themes_names(self, obj):
        return ", ".join([ct.name for ct in obj.color_themes.all()]) if obj.color_themes.exists() else "—"
    color_themes_names.short_description = "Оттенки"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'name', 'address', 'delivery_date', 'phone_number', 'status', 'product_name']
    list_filter = ['status']
    def product_name(self, obj):
        return obj.product.name if obj.product else "—"

    product_name.short_description = "Букет"
