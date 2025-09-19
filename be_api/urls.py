from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    # Products
    product_list, product_create, product_detail,
    # Stocks
    daily_stock_list, daily_stock_create, daily_stock_detail, daily_stock_summary,daily_stock_update,
    # Bills
    bill_list, bill_create, bill_detail, bill_update, bill_delete,
    # Employee Consumption
    consumption_list, consumption_create, consumption_detail, consumption_update, consumption_delete,
    # Business Info
    business_info_get, business_info_update,low_stock_alert,
    # Auth
    CustomTokenObtainPairView,LoginView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # JWT Auth
    path('login/', LoginView.as_view(), name="login"),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Products CRUD
    path('products/', product_list, name='product_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),  # <-- GET, PUT, DELETE


    # Daily Stocks CRUD
    path('stocks/', daily_stock_list, name='daily_stock_list'),
    path('stocks/create/', daily_stock_create, name='daily_stock_create'),
    path('stocks/<int:stock_id>/', daily_stock_detail, name='daily_stock_detail'),  # GET, PATCH, DELETE
    path('stocks/<int:stock_id>/update/', daily_stock_update, name='daily_stock_update'),  # PATCH only for Added Stock
    path('stocks/summary/', daily_stock_summary, name='daily_stock_summary'),


    # Bills CRUD
    path('bills/', bill_list, name='bill_list'),
    path('bills/create/', bill_create, name='bill_create'),
    path('bills/<int:bill_id>/', bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/update/', bill_update, name='bill_update'),
    path('bills/<int:bill_id>/delete/', bill_delete, name='bill_delete'),

    # Employee Consumption CRUD
    path('consumptions/', consumption_list, name='consumption_list'),
    path('consumptions/create/', consumption_create, name='consumption_create'),
    path('consumptions/<int:consumption_id>/', consumption_detail, name='consumption_detail'),
    path('consumptions/<int:consumption_id>/update/', consumption_update, name='consumption_update'),
    path('consumptions/<int:consumption_id>/delete/', consumption_delete, name='consumption_delete'),

    # Business Info
    path('business-info/', business_info_get, name='business_info_get'),
    path('business-info/update/', business_info_update, name='business_info_update'),
    
    path('stocks/low-stock-alert/', low_stock_alert, name='low_stock_alert'),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
