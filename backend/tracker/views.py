from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stock, PortfolioItem, PriceAlert
from .serializers import StockSerializer, PortfolioItemSerializer, PriceAlertSerializer
from .services import update_stock_info

from django.views.generic import TemplateView, ListView, CreateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Stock, PortfolioItem, PriceAlert
from .serializers import StockSerializer, PortfolioItemSerializer, PriceAlertSerializer
from .services import update_stock_info

# --- UI Views (Template Based) ---

class DashboardView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'tracker/dashboard.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Stock.objects.filter(symbol__icontains=query)
        return Stock.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

    def post(self, request, *args, **kwargs):
        # Quick Add Stock form handler
        symbol = request.POST.get('symbol')
        if symbol:
            stock, created = Stock.objects.get_or_create(symbol=symbol.upper())
            if created:
                try:
                    update_stock_info(stock.id)
                except Exception:
                    pass 
        return redirect('dashboard')

class PortfolioListView(LoginRequiredMixin, ListView):
    model = PortfolioItem
    template_name = 'tracker/portfolio.html'
    context_object_name = 'items'

    def post(self, request, *args, **kwargs):
        # Add to portfolio
        stock_symbol = request.POST.get('stock_symbol')
        price = request.POST.get('price')
        qty = request.POST.get('quantity')
        
        try:
            stock = Stock.objects.get(symbol=stock_symbol.upper())
            PortfolioItem.objects.create(
                stock=stock,
                purchase_price=price,
                quantity=qty
            )
        except Stock.DoesNotExist:
            pass # Error handling skipped for brevity
            
        return redirect('portfolio')

class AlertListView(LoginRequiredMixin, ListView):
    model = PriceAlert
    template_name = 'tracker/alerts.html'
    context_object_name = 'alerts'
    ordering = ['-date']

class UpdateTargetView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from django.http import JsonResponse
        
        stock = get_object_or_404(Stock, pk=pk)
        new_target = request.POST.get('target_drop')
        
        if new_target:
            try:
                stock.target_drop_percent = float(new_target)
                stock.save()
                return JsonResponse({'status': 'success', 'new_value': stock.target_drop_percent})
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid value'}, status=400)
        
        return JsonResponse({'status': 'error', 'message': 'No value provided'}, status=400)

# --- API Views ---

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def perform_create(self, serializer):
        stock = serializer.save()
        # Initial fetch
        try:
            update_stock_info(stock.id)
        except Exception as e:
            # If fetching fails, we still keep the stock but maybe log error
            print(f"Error fetching initial data: {e}")

    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        stock = self.get_object()
        try:
            update_stock_info(stock.id)
            stock.refresh_from_db()
            serializer = self.get_serializer(stock)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PortfolioItemViewSet(viewsets.ModelViewSet):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer

class PriceAlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceAlert.objects.all().order_by('-date')
    serializer_class = PriceAlertSerializer
