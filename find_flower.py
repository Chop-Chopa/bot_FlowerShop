import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowershop.settings")
django.setup()


from admin_flowershop.models import  Product

user_data = {
    'occasion': 'День рождения',
    'flower_color': '',
    'price': 500,
}


def find_flower():
    queryset = Product.objects.filter(available=True)

    if user_data.get("occasion"):
        queryset = queryset.filter(categories__name=user_data["occasion"])

    if user_data.get("flower_color"):
        queryset = queryset.filter(color_themes__name=user_data["flower_color"])

    if user_data.get("price"):
        queryset = queryset.filter(price__range=(user_data["price"]-500, user_data["price"]+500))
    elif user_data.get("price")=='Больше':
        queryset = queryset.filter(price__gt=2000)

    return queryset.order_by("?").first()



