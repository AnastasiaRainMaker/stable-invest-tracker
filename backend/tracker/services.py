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
    
    from_email = settings.ALERT_FROM_EMAIL
    recipient_list = [settings.ALERT_RECIPIENT_EMAIL]
    
    send_mail(subject, message, from_email, recipient_list)
    
def discover_top_stocks():
    # In a real app, this might scrape a screener. 
    # For this demo, we check a curated list of known 'solid' companies.
    candidates = [
        # Tech / Comm Services
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "ADBE", "CRM", "CSCO",
        "NFLX", "AMD", "QCOM", "INTC", "TXN", "HON", "IBM", "ORCL", "ACN", "INTU",
        "NOW", "UBER", "ABNB", "PANW", "SNOW", "PLTR", "FTNT", "ZM", "WDAY", "ADSK",
        "KLAC", "LRCX", "AMAT", "MU", "ADI", "NXPI", "MCHP", "GLW", "HPQ", "DELL",
        "TEL", "APH", "KEYS", "TRMB", "TER", "STX", "WDC", "NTAP", "PSTG", "FSLR",
        
        # Finance
        "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "C", "GS", "MS", "AXP",
        "BLK", "SPGI", "MCO", "SCHW", "MMC", "AON", "PGR", "CB", "USB", "PNC",
        "TFC", "COF", "FITB", "STT", "BK", "NTRS", "RF", "KEY", "CFG", "HBAN",
        "ALL", "TRV", "HIG", "CINF", "PFG", "MET", "PRU", "LNC", "AIG", "PYPL",
        
        # Healthcare
        "JNJ", "UNH", "LLY", "PFE", "ABBV", "MRK", "TMO", "DHR", "ABT", "BMY",
        "AMGN", "GILD", "CVS", "CI", "ELV", "HCA", "SYK", "ISRG", "EW", "BSX",
        "BDX", "ZTS", "REGN", "VRTX", "BIIB", "ILMN", "DXCM", "A", "MTD", "WAT",
        "IQV", "CNC", "HUM", "MCK", "CAH", "ABC", "BAX", "HPQ", "ALGN", "RMD",
        
        # Consumer / Retail
        "AMZN", "WMT", "COST", "HD", "LOW", "MCD", "SBUX", "NKE", "TGT", "TJX",
        "ROST", "LULU", "MAR", "HLT", "BKNG", "EXPE", "RCL", "CCL", "YUM", "CMG",
        "DRI", "DPZ", "TSCO", "DG", "DLTR", "BBY", "KMX", "AZO", "ORLY", "AAP",
        "KO", "PEP", "PG", "PM", "MO", "CL", "EL", "KMB", "GIS", "K",
        "MDLZ", "HSY", "STZ", "TAP", "CAG", "CPB", "SJM", "TSN", "HRL", "MKC",
        
        # Industrial / Energy / Materials
        "CAT", "DE", "HON", "GE", "MMM", "UNP", "UPS", "FDX", "LMT", "RTX",
        "BA", "GD", "NOC", "LHX", "TXT", "HII", "ETN", "ITW", "EMR", "PH",
        "CMI", "PCAR", "GWW", "FAST", "URI", "XYL", "ROK", "AME", "DOV", "SWK",
        "XOM", "CVX", "COP", "SLB", "EOG", "PXD", "OXY", "HES", "HAL", "BKR",
        "LIN", "APD", "ECL", "SHW", "PPG", "NUE", "FCX", "DOW", "DD", "CTVA",
        
        # Utilities / Real Estate
        "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "PEG", "ED",
        "PLD", "AMT", "CCI", "EQIX", "PSA", "O", "SPG", "WELL", "DLR", "VTR"
    ]
    
    print(f"Scanning {len(candidates)} candidates for long-term stability...")
    
    discovered = []
    
    for symbol in candidates:
        try:
            # Check if we already track it
            if Stock.objects.filter(symbol=symbol).exists():
                continue
                
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5y") # 5 years for long term
            
            if hist.empty:
                continue
                
            # Logic:
            # 1. Positive Growth (Current > 5yr ago)
            # 2. Low Volatility (std dev of returns)
            
            start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            
            if current_price <= start_price:
                continue # No growth in 5 years, skip
                
            hist['Returns'] = hist['Close'].pct_change()
            volatility = hist['Returns'].std() * np.sqrt(252)
            
            # Strict stability for "Top 100": < 30% volatility
            if volatility < 0.30:
                print(f"Found gem: {symbol} (Vol: {volatility:.2f})")
                
                stock, created = Stock.objects.get_or_create(symbol=symbol)
                stock.name = ticker.info.get('longName', symbol)
                stock.is_stable = True
                stock.current_price = current_price
                stock.last_checked = timezone.now()
                stock.save()
                discovered.append(stock)
                
        except Exception as e:
            print(f"Skipping {symbol}: {e}")
            
    return discovered

