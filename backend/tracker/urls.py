from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, PortfolioItemViewSet, PriceAlertViewSet
from .views import DashboardView, PortfolioListView, AlertListView

router = DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'portfolio', PortfolioItemViewSet)
router.register(r'alerts', PriceAlertViewSet)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('portfolio/', PortfolioListView.as_view(), name='portfolio'),
    path('alerts/', AlertListView.as_view(), name='alerts'),
    path('api/', include(router.urls)),
]
