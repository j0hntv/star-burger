from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import DecimalField, F, Sum
from django.utils import timezone
from django.utils.html import format_html
from geopy.distance import distance

from .utils import add_coordinates


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingridients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class QuerySetOrder(models.QuerySet):
    def total_price(self):
        return self.annotate(
            total_price=Sum(F('order_items__price') * F('order_items__quantity'), output_field=DecimalField())
        )


class Order(models.Model):
    STATUSES = (
        ('PROCESSED', 'Обработанный'),
        ('UNPROCESSED', 'Необработанный'),
    )
    PAYMENTS = (
        ('CASH', 'Наличные'),
        ('NONCASH', 'Электронно'),
    )
    address = models.CharField('Адрес доставки', max_length=100)
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = models.CharField('Номер телефона', max_length=50)
    status = models.CharField('Статус заказа', max_length=15, choices=STATUSES, default='UNPROCESSED')
    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField('Время заказа', default=timezone.now, blank=True)
    called_at = models.DateTimeField('Время звонка', blank=True, null=True)
    delivered_at = models.DateTimeField('Время доставки', blank=True, null=True)
    payment = models.CharField('Способ оплаты', max_length=15, choices=PAYMENTS, default='CASH')

    objects = QuerySetOrder.as_manager()

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-status',)

    def get_order_restaurants(self):
        products = [order_item.product for order_item in self.order_items.all()]
        menu_items = [product.menu_items.all() for product in products]
        restaurants = [set([restaurants.restaurant for restaurants in menu_item]) for menu_item in menu_items]
        return list(set.intersection(*restaurants))

    def get_order_restaurants_with_distances(self):
        restaurants = add_coordinates(self.get_order_restaurants()) # similar queries
        return {restaurant: distance(restaurant.coordinates, self.coordinates).km for restaurant in restaurants}


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(verbose_name='Количество', validators=[MinValueValidator(1), MaxValueValidator(50)])
    price = models.DecimalField('Стоимость заказа', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'


class Banner(models.Model):
    image = models.ImageField('Картинка', upload_to='banners')
    title = models.CharField('Название', max_length=50)
    text = models.TextField('Описание')
    is_active = models.BooleanField('Показывать', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    def get_preview(self):
        return format_html(f'<img src="{self.image.url}" width="500" />')

    get_preview.short_description = 'Просмотр'
