from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, PortfolioItemViewSet, PriceAlertViewSet
from .views import DashboardView, PortfolioListView, AlertListView, UpdateTargetView

router = DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'portfolio', PortfolioItemViewSet)
router.register(r'alerts', PriceAlertViewSet)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('portfolio/', PortfolioListView.as_view(), name='portfolio'),
    path('alerts/', AlertListView.as_view(), name='alerts'),
    path('stock/<int:pk>/update-target/', UpdateTargetView.as_view(), name='update_target'),
    path('api/', include(router.urls)),
]
