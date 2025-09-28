import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowershop.settings")
django.setup()

import random
from decimal import Decimal
from admin_flowershop.models import Product


def find_flower(user_data):
    qs = Product.objects.filter(available=True)

    occasion = user_data.get("occasion")
    if occasion:
        qs = qs.filter(categories__name__iexact=occasion)

    flower_color = user_data.get("flower_color")
    if flower_color:
        qs = qs.filter(color_themes__name__iexact=flower_color)

    price_value = user_data.get("price")
    if price_value:
        if price_value == 'Больше':
            qs = qs.filter(price__gt=2000)
        else:
            p = int(price_value)
            qs = qs.filter(price__range=(Decimal(p - 500), Decimal(p + 500)))

    qs = qs.distinct()

    qs = qs.prefetch_related('color_themes', 'categories').only(
        'id', 'name', 'price', 'image', 'description', 'composition'
    )

    count = qs.count()
    if count == 0:
        return None

    idx = random.randrange(count)
    return qs[idx]




