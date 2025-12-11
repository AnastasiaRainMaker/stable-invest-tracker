from django.db import models
from django.utils import timezone
import datetime

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_stable = models.BooleanField(default=False)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_drop_percent = models.FloatField(default=10.0)
    last_checked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol

class PortfolioItem(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='portfolio_items')
    purchase_date = models.DateField(default=datetime.date.today)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)

    def __str__(self):
        return f"{self.stock.symbol} - {self.purchase_date}"

class PriceAlert(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    date = models.DateTimeField(auto_now_add=True)
    price_at_alert = models.DecimalField(max_digits=10, decimal_places=2)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.stock.symbol} at {self.price_at_alert}"
