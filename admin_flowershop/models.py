from django.db import models

class ColorTheme(models.Model):
    name = models.CharField(max_length=100, verbose_name='Цветовая гамма')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Оттенок'
        verbose_name_plural = 'Оттенки'

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Категория букета')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название букета')
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категория букета',
        blank=True,
        related_name='products',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField()
    description = models.TextField(verbose_name='Описание/смысл букета')
    available = models.BooleanField(default=True, verbose_name='Наличие')
    composition = models.TextField(blank=True, null=True, verbose_name='Цветочный состав')
    color_themes = models.ManyToManyField(
        ColorTheme,
        blank=True,
        related_name="products"
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def __str__(self):
        return f"{self.name} — {self.price} руб."


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("in_progress", "В работе"),
        ("completed", "Выполнен"),
    ]

    customer_id = models.BigIntegerField(verbose_name="Telegram ID клиента")
    name = models.CharField(max_length=100, verbose_name='ФИО клиента')
    address = models.TextField(verbose_name='Адрес')
    delivery_date = models.TextField(verbose_name="Дата доставки")
    phone_number = models.CharField("Телефон клиента", max_length=20)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ {self.id} — {self.name}"