from django.db import models


class Place(models.Model):
    address = models.CharField('Адрес', max_length=128, unique=True)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
