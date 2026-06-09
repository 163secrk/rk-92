from rest_framework import serializers
from .models import Wine, ValuationHistory, CollectionStats
from decimal import Decimal


class WineSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appreciation_rate = serializers.FloatField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_cost = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    maturity = serializers.SerializerMethodField()
    maturity_display = serializers.SerializerMethodField()

    class Meta:
        model = Wine
        fields = '__all__'

    def get_maturity(self, obj):
        return obj.get_current_maturity()

    def get_maturity_display(self, obj):
        status_map = {
            'cellared': '窖藏中',
            'drinking': '适饮期',
            'peak': '巅峰期',
            'declining': '衰退期'
        }
        return status_map.get(obj.get_current_maturity(), '未知')


class WineListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appreciation_rate = serializers.FloatField(read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    maturity_display = serializers.SerializerMethodField()

    class Meta:
        model = Wine
        fields = ['id', 'name', 'chateau', 'vintage', 'category', 'category_display',
                  'quantity', 'purchase_price', 'current_value', 'appreciation_rate',
                  'total_value', 'status', 'status_display', 'maturity_display',
                  'country', 'region', 'image_url']

    def get_maturity_display(self, obj):
        status_map = {
            'cellared': '窖藏中',
            'drinking': '适饮期',
            'peak': '巅峰期',
            'declining': '衰退期'
        }
        return status_map.get(obj.get_current_maturity(), '未知')


class ValuationHistorySerializer(serializers.ModelSerializer):
    wine_name = serializers.CharField(source='wine.name', read_only=True)

    class Meta:
        model = ValuationHistory
        fields = '__all__'


class CollectionStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionStats
        fields = '__all__'
