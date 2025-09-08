from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import *
from .serializers import *

# be_api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .token import get_tokens_for_user

class LoginView(APIView):
    permission_classes = [AllowAny]  # 🔥 very important

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response({
                **tokens,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,  # custom field
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
# be_api/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

        


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, DailyStock, Bill, BillItem, EmployeeConsumption, BusinessInfo
from .serializers import (
    ProductSerializer, DailyStockSerializer, BillSerializer, BillItemSerializer,
    EmployeeConsumptionSerializer, BusinessInfoSerializer
)

# ------------------------- PRODUCTS -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    serializer = ProductSerializer(Product.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return Response({"detail":"Deleted"}, status=200)



# ------------------------- DAILY STOCKS -------------------------
# ------------------------- DAILY STOCK -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_stock_list(request):
    serializer = DailyStockSerializer(DailyStock.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def daily_stock_create(request):
    product_id = request.data.get("product_id")
    stock_date = request.data.get("stock_date")

    if DailyStock.objects.filter(product_id=product_id, stock_date=stock_date).exists():
        return Response({"error": "Stock for this product and date already exists"}, status=400)

    serializer = DailyStockSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def daily_stock_detail(request, stock_id):
    try:
        stock = DailyStock.objects.get(id=stock_id)
    except DailyStock.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)

    if request.method == 'GET':
        serializer = DailyStockSerializer(stock)
        return Response(serializer.data)

    elif request.method in ['PUT','PATCH']:
        serializer = DailyStockSerializer(stock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        stock.delete()
        return Response({"detail":"Deleted"}, status=200)

# ------------------------- BILLS -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list(request):
    serializer = BillSerializer(Bill.objects.all(), many=True)
    return Response(serializer.data)

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Bill, BillItem, Product, DailyStock
from .serializers import BillSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_create(request):
    data = request.data
    items = data.get('items', [])
    total = 0
    tax_rate = data.get('tax_rate', 0.10)

    bill = Bill.objects.create(
        section = data.get('section','customer'),
        payment_method = data.get('payment_method','cash'),
        total=0,
        tax=0
    )

    for item in items:
        try:
            product = Product.objects.get(id=item['product'])
        except Product.DoesNotExist:
            continue

        quantity = int(item['quantity'])
        subtotal = product.price * quantity

        # Create BillItem
        BillItem.objects.create(
            bill=bill,
            product=product,
            quantity=quantity,
            price=subtotal
        )

        # Update total_sold
        product.total_sold += quantity
        product.save()

        # Update daily stock if needed
        if product.stock_type == 'daily_stock':
            today = timezone.now().date()
            daily_stock, _ = DailyStock.objects.get_or_create(product=product, stock_date=today)
            daily_stock.sold_quantity += quantity
            daily_stock.save()

        total += subtotal

    tax = total * tax_rate
    bill.total = total + tax
    bill.tax = tax
    bill.save()

    serializer = BillSerializer(bill)
    return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_detail(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    serializer = BillSerializer(bill)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bill_update(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    serializer = BillSerializer(bill, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bill_delete(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    bill.delete()
    return Response({"detail":"Deleted"}, status=200)

# ------------------------- EMPLOYEE CONSUMPTION -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consumption_list(request):
    serializer = EmployeeConsumptionSerializer(EmployeeConsumption.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def consumption_create(request):
    data = request.data
    data['user'] = request.user.id
    serializer = EmployeeConsumptionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        # Update product sold
        product = Product.objects.get(id=data['product'])
        product.total_sold += int(data['quantity'])
        product.save()
        # Update daily stock
        if product.stock_type=='daily_stock':
            today = timezone.now().date()
            daily_stock, _ = DailyStock.objects.get_or_create(product=product, date=today)
            daily_stock.sold_stock += int(data['quantity'])
            daily_stock.remaining_stock -= int(data['quantity'])
            daily_stock.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consumption_detail(request, consumption_id):
    try:
        c = EmployeeConsumption.objects.get(id=consumption_id)
    except EmployeeConsumption.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    serializer = EmployeeConsumptionSerializer(c)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def consumption_update(request, consumption_id):
    try:
        c = EmployeeConsumption.objects.get(id=consumption_id)
    except EmployeeConsumption.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    serializer = EmployeeConsumptionSerializer(c, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def consumption_delete(request, consumption_id):
    try:
        c = EmployeeConsumption.objects.get(id=consumption_id)
    except EmployeeConsumption.DoesNotExist:
        return Response({"detail":"Not found"}, status=404)
    c.delete()
    return Response({"detail":"Deleted"}, status=200)

# ------------------------- BUSINESS INFO -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def business_info_get(request):
    obj, _ = BusinessInfo.objects.get_or_create(id=1)
    serializer = BusinessInfoSerializer(obj)
    return Response(serializer.data)

@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def business_info_update(request):
    obj, _ = BusinessInfo.objects.get_or_create(id=1)
    serializer = BusinessInfoSerializer(obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

# ---------------------- STOCK SUMMARY ----------------------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import DailyStock

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_stock_summary(request):
    """
    Returns a summary of stock for a given date (default: today)
    - total_products: total number of products in inventory
    - total_sold: total sold quantity
    - total_remaining: total remaining stock
    - stock_details: list of {product_name, sold_quantity, remaining_stock}
    """
    date = request.query_params.get("date")
    if not date:
        from datetime import date as dt
        date = dt.today().isoformat()

    stocks = DailyStock.objects.filter(stock_date=date)
    
    total_products = stocks.count()
    total_sold = stocks.aggregate(total=Sum('sold_quantity'))['total'] or 0
    total_remaining = stocks.aggregate(total=Sum('remaining_stock'))['total'] or 0
    
    stock_details = []
    for stock in stocks:
        stock_details.append({
            "product_name": stock.product.name,
            "sold_quantity": stock.sold_quantity,
            "remaining_stock": stock.remaining_stock,
        })
    
    return Response({
        "date": date,
        "total_products": total_products,
        "total_sold": total_sold,
        "total_remaining": total_remaining,
        "stock_details": stock_details,
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import DailyStock, Product
from .serializers import DailyStockSerializer
from django.db.models import Sum

from django.db.models import F, Sum, ExpressionWrapper, IntegerField

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_stock_summary(request):
    date = request.GET.get('date')
    if not date:
        return Response({"error": "date is required"}, status=400)

    stocks = DailyStock.objects.filter(stock_date=date)

    total_products = stocks.count()
    total_sold = stocks.aggregate(total_sold=Sum('sold_quantity'))['total_sold'] or 0
    total_remaining = stocks.aggregate(
        total_remaining=Sum(F('starting_stock') + F('added_stock'))
        - Sum('sold_quantity')
    )['total_remaining'] or 0

    # Calculate low stock correctly
    low_stock_count = stocks.annotate(
        total_stock=ExpressionWrapper(F('starting_stock') + F('added_stock'), output_field=IntegerField())
    ).filter(total_stock__lt=10).count()

    return Response({
        "total_products": total_products,
        "total_sold": total_sold,
        "total_remaining": total_remaining,
        "low_stock_count": low_stock_count
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def daily_stock_update(request, stock_id):
    try:
        stock = DailyStock.objects.get(id=stock_id)
    except DailyStock.DoesNotExist:
        return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
    
    added_stock = request.data.get("added_stock")
    if added_stock is not None:
        stock.added_stock = int(added_stock)
        stock.save()
        serializer = DailyStockSerializer(stock)
        return Response(serializer.data)
    
    return Response({"error": "added_stock field is required"}, status=status.HTTP_400_BAD_REQUEST)
