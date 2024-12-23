from django.db import models


# Create your models here.
class BinanceSpotKlineDaily(models.Model):
    current_time = models.DateTimeField()
    symbol = models.CharField(max_length=255)
    open_time = models.CharField(max_length=255)
    open_time_date = models.DateTimeField()
    open = models.DecimalField(max_digits=50,decimal_places=8)
    high = models.DecimalField(max_digits=50,decimal_places=8)
    low = models.DecimalField(max_digits=50,decimal_places=8)
    close = models.DecimalField(max_digits=50,decimal_places=8)
    volume = models.DecimalField(max_digits=50,decimal_places=8)
    close_time = models.CharField(max_length=255)
    close_time_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=50, decimal_places=8)
    number_of_trades = models.DecimalField(max_digits=50, decimal_places=8)
    buy_volume = models.DecimalField(max_digits=50, decimal_places=8)
    buy_amount = models.DecimalField(max_digits=50, decimal_places=8)

class BinanceSpotKline1m(models.Model):
    current_time = models.DateTimeField()
    symbol = models.CharField(max_length=255)
    open_time = models.CharField(max_length=255)
    open_time_date = models.DateTimeField()
    open = models.DecimalField(max_digits=50,decimal_places=8)
    high = models.DecimalField(max_digits=50,decimal_places=8)
    low = models.DecimalField(max_digits=50,decimal_places=8)
    close = models.DecimalField(max_digits=50,decimal_places=8)
    volume = models.DecimalField(max_digits=50,decimal_places=8)
    close_time = models.CharField(max_length=255)
    close_time_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=50, decimal_places=8)
    number_of_trades = models.DecimalField(max_digits=50, decimal_places=8)
    buy_volume = models.DecimalField(max_digits=50, decimal_places=8)
    buy_amount = models.DecimalField(max_digits=50, decimal_places=8)


