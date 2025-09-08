from rest_framework import serializers
from .models import *

# User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','email','role']

# Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# DailyStock Serializer
# be_api/serializers.py
from rest_framework import serializers
from .models import DailyStock

from rest_framework import serializers
from .models import DailyStock, Product

class ProductNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']  # we need id and name

# serializers.py
class DailyStockSerializer(serializers.ModelSerializer):
    product = ProductNestedSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = DailyStock
        fields = ['id', 'product', 'product_id', 'stock_date', 'starting_stock', 'added_stock', 'sold_quantity', 'low_stock_threshold']





# BillItem
class BillItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = BillItem
        fields = '__all__'

# Bill
class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    class Meta:
        model = Bill
        fields = '__all__'

# Employee Consumption
class EmployeeConsumptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = EmployeeConsumption
        fields = '__all__'

# Printer Setting
class PrinterSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterSetting
        fields = '__all__'

# Business Info
class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = '__all__'
# be_api/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims inside token
        token['role'] = user.role  # assumes you have a `role` field in CustomUser
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user info in response body
        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "role": self.user.role
        }
        return data
