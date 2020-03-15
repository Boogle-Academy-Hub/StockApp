from django.db import models

# Create your models here.
class StockPrice(models.Model):
    ticker = models.CharField(max_length=64)
    open_price = models.FloatField()
    close_price = models.FloatField()
    realtime_price = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)