import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowershop.settings")

django.setup()

from admin_flowershop.models import Order, Product

def create_order_from_context(user_id, user_data):
    """
    Создаёт заказ в базе данных на основе собранных данных от клиента.
    """
    product = None
    if user_data.get("product_id"):
        try:
            product = Product.objects.get(id=user_data["product_id"])
        except Product.DoesNotExist:
            product = None

    order = Order.objects.create(
        customer_id=user_id,
        name=user_data.get("name", ""),
        address=user_data.get("address", ""),
        delivery_date=user_data.get("date_time", ""),
        phone_number=user_data.get("phone", ""),
        product=product,
    )
    return order