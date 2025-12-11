from django.core.management.base import BaseCommand
from tracker.models import Stock
from tracker.services import update_stock_info, discover_top_stocks
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Runs scheduled maintenance: Price Checks and Weekly Discovery'

    def add_arguments(self, parser):
        parser.add_argument('--weekly', action='store_true', help='Run weekly discovery task')

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled Tasks...")
        
        # 1. Price Checks (Daily)
        stocks = Stock.objects.all()
        for stock in stocks:
            try:
                update_stock_info(stock.id)
                self.stdout.write(f"Updated {stock.symbol}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed {stock.symbol}: {e}"))
                
        # 2. Discovery (Weekly)
        if options['weekly']:
            self.stdout.write("Running Weekly Discovery...")
            found = discover_top_stocks()
            self.stdout.write(self.style.SUCCESS(f"Discovered {len(found)} new stable stocks."))
            
        self.stdout.write(self.style.SUCCESS('Done.'))
