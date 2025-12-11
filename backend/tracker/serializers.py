from rest_framework import serializers
from .models import Stock, PortfolioItem, PriceAlert

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('is_stable', 'current_price', 'last_checked', 'created_at')

class PortfolioItemSerializer(serializers.ModelSerializer):
    stock_details = StockSerializer(source='stock', read_only=True)
    
    class Meta:
        model = PortfolioItem
        fields = '__all__'

class PriceAlertSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    
    class Meta:
        model = PriceAlert
        fields = '__all__'
