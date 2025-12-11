import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tracker.models import Stock, PriceAlert
from tracker.services import check_price_alert

def test_alert():
    print("Testing Alert Logic...")
    
    # Create or Get Stock
    stock, created = Stock.objects.get_or_create(symbol="TEST", defaults={"name": "Test Stock"})
    
    # Set Fake Data
    # 52w High = 100.
    # We want a 10% drop, so current price should be <= 90.
    stock.current_price = 85.00 
    stock.target_drop_percent = 10.0
    stock.save()
    
    # Mock ticker info
    class MockTicker:
        @property
        def info(self):
            return {'fiftyTwoWeekHigh': 100.0}
            
    # Run Check
    print("Running check...")
    check_price_alert(stock, ticker_obj=MockTicker())
    
    # Verify Alert
    alerts = PriceAlert.objects.filter(stock=stock)
    print(f"Alerts found: {alerts.count()}")
    if alerts.exists():
        print(f"Alert Price: {alerts.first().price_at_alert}")
        print(f"Alert Sent: {alerts.first().sent}")

if __name__ == "__main__":
    test_alert()
