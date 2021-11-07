from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = PhoneNumberField(
        'контактный телефон',
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_price(self):
        return self.annotate(
            price=Sum(F('items__quantity') * F('items__price'))
        )
    def unprocessed(self):
        return self.filter(status='UNPROCESSED')


class Order(models.Model):
    STATUS_CHOICES = (
        ('PROCESSED', 'Обработанный'),
        ('UNPROCESSED', 'Необработанный'),
    )
    firstname = models.CharField('Имя', max_length=32)
    lastname = models.CharField('Фамилия', max_length=32)
    address = models.CharField('Адрес', max_length=128)
    phonenumber = PhoneNumberField('Телефон')
    status = models.CharField('Статус заказа', max_length=16, choices=STATUS_CHOICES, default='UNPROCESSED')
    comment = models.TextField('Комментарий', blank=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    objects = OrderQuerySet.as_manager()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(verbose_name='Количество', validators=[MinValueValidator(0)])
    price = models.DecimalField(verbose_name='Цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.product} - {self.quantity} шт.'

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
