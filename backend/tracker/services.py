import yfinance as yf
from .models import Stock, PriceAlert
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import numpy as np

def update_stock_info(stock_id):
    stock = Stock.objects.get(id=stock_id)
    ticker = yf.Ticker(stock.symbol)
    
    # Get basic info
    info = ticker.info
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    stock.name = info.get('longName', stock.symbol)
    stock.current_price = current_price
    stock.last_checked = timezone.now()
    
    # Stability Analysis
    # Get 2 years of history
    hist = ticker.history(period="2y")
    if not hist.empty:
        # Calculate daily returns
        hist['Returns'] = hist['Close'].pct_change()
        # Annualized Volatility
        volatility = hist['Returns'].std() * np.sqrt(252)
        
        # Threshold for stability (e.g., 20% volatility or less)
        # Low volatility implies stability.
        stock.is_stable = volatility < 0.20
    
    stock.save()
    
    # Check for alerts
    if current_price:
        check_price_alert(stock, ticker)

def check_price_alert(stock, ticker_obj=None):
    if not ticker_obj:
        ticker_obj = yf.Ticker(stock.symbol)
    
    info = ticker_obj.info
    year_high = info.get('fiftyTwoWeekHigh')
    current_price = stock.current_price
    
    if year_high and current_price:
        # Check drop from high
        drop_percent = ((year_high - float(current_price)) / year_high) * 100
        
        if drop_percent >= stock.target_drop_percent:
            # Check if we already sent an alert recently (e.g., today)
            recent_alert = PriceAlert.objects.filter(
                stock=stock, 
                date__gte=timezone.now() - timedelta(days=1)
            ).exists()
            
            if not recent_alert:
                alert = PriceAlert.objects.create(
                    stock=stock,
                    price_at_alert=current_price,
                    sent=False # Will set true after sending
                )
                send_price_alert_email(alert, drop_percent, year_high)

def send_price_alert_email(alert, drop_percent, year_high):
    subject = f"Price Alert: {alert.stock.symbol} Down {drop_percent:.1f}%"
    message = (
        f"The stock {alert.stock.name} ({alert.stock.symbol}) has dropped {drop_percent:.1f}% "
        f"from its 52-week high of {year_high}.\n\n"
        f"Current Price: {alert.price_at_alert}\n"
        f"Target Drop: {alert.stock.target_drop_percent}%\n\n"
        f"This might be a buying opportunity for this stable asset."
    )
    
    from_email = 'system@stableinvest.local'
    recipient_list = ['user@example.com'] # In real app, this would be the user's email
    
    send_mail(subject, message, from_email, recipient_list)
    
    alert.sent = True
    alert.save()
