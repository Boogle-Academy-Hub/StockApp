from django.urls import path
from . import views
from .views import trading_volume, live_price, price_history

urlpatterns = [
    path('', views.live_price, name='live_price'),
    path('trading-volume', views.trading_volume, name='trading_volume'),
    path('price-history', views.price_history, name='price_history')
]