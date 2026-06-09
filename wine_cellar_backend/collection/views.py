from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from .models import Wine, ValuationHistory, CollectionStats
from .serializers import WineSerializer, WineListSerializer, ValuationHistorySerializer, CollectionStatsSerializer
import numpy as np


class WineViewSet(viewsets.ModelViewSet):
    queryset = Wine.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return WineListSerializer
        return WineSerializer

    def get_queryset(self):
        queryset = Wine.objects.all()
        category = self.request.query_params.get('category')
        status = self.request.query_params.get('status')
        country = self.request.query_params.get('country')
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        if country:
            queryset = queryset.filter(country=country)
        return queryset

    def perform_create(self, serializer):
        wine = serializer.save()
        ValuationHistory.objects.create(
            wine=wine,
            value=wine.current_value,
            change_percent=0,
            reason='初始估值'
        )

    @action(detail=True, methods=['post'])
    def valuate(self, request, pk=None):
        wine = self.get_object()
        years_aged = timezone.now().year - wine.vintage
        base_appreciation = 0.03
        vintage_factor = 1.0
        rare_vintages = {2010, 2015, 2016, 2018, 2019, 2020}

        if wine.vintage in rare_vintages:
            vintage_factor = 1.5

        if wine.category == 'red' and 'Bordeaux' in wine.region:
            base_appreciation = 0.05
        elif wine.category == 'red' and 'Burgundy' in wine.region:
            base_appreciation = 0.06
        elif wine.category == 'sparkling' and 'Champagne' in wine.region:
            base_appreciation = 0.04

        appreciation_rate = base_appreciation * years_aged * vintage_factor
        new_value = wine.purchase_price * Decimal(1 + appreciation_rate)

        if wine.get_current_maturity() == 'peak':
            new_value *= Decimal('1.15')
        elif wine.get_current_maturity() == 'declining':
            new_value *= Decimal('0.9')

        change_percent = ((new_value - wine.current_value) / wine.current_value * 100 if wine.current_value > 0 else 0)
        wine.current_value = new_value
        wine.save()

        ValuationHistory.objects.create(
            wine=wine,
            value=new_value,
            change_percent=float(change_percent),
            reason='自动估值',
            notes=f'年份因素: {vintage_factor}, 基础升值率: {base_appreciation * 100}%'
        )

        return Response({
            'wine': WineSerializer(wine).data,
            'valuation': ValuationHistorySerializer(
                ValuationHistory.objects.filter(wine=wine).first()
            ).data,
        })

    @action(detail=True, methods=['get'])
    def valuation_history(self, request, pk=None):
        wine = self.get_object()
        history = wine.valuations.all()
        return Response(ValuationHistorySerializer(history, many=True).data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('q', '')
        queryset = Wine.objects.filter(name__icontains=keyword) | \
                   Wine.objects.filter(chateau__icontains=keyword) | \
                   Wine.objects.filter(region__icontains=keyword)
        return Response(WineListSerializer(queryset, many=True).data)


class ValuationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ValuationHistory.objects.all()
    serializer_class = ValuationHistorySerializer


class CollectionStatsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def overview(self, request):
        wines = Wine.objects.exclude(status__in=['sold', 'mortgaged'])
        total_bottles = wines.aggregate(total=Sum('quantity'))['total'] or 0
        
        wines_with_total = wines.annotate(
            total_value_expr=ExpressionWrapper(
                F('current_value') * F('quantity'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            total_cost_expr=ExpressionWrapper(
                F('purchase_price') * F('quantity'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        
        total_value = wines_with_total.aggregate(total=Sum('total_value_expr'))['total'] or 0
        total_cost = wines_with_total.aggregate(total=Sum('total_cost_expr'))['total'] or 0

        if total_cost > 0:
            appreciation_rate = float((total_value - total_cost) / total_cost * 100)
        else:
            appreciation_rate = 0

        by_category = {}
        for cat, _ in Wine.CATEGORY_CHOICES:
            cat_wines = wines_with_total.filter(category=cat)
            by_category[cat] = {
                'count': cat_wines.aggregate(total=Sum('quantity'))['total'] or 0,
                'value': float(cat_wines.aggregate(total=Sum('total_value_expr'))['total'] or 0),
            }

        by_country = {}
        countries = wines.values_list('country', flat=True).distinct()
        for country in countries:
            country_wines = wines_with_total.filter(country=country)
            by_country[country] = {
                'count': country_wines.aggregate(total=Sum('quantity'))['total'] or 0,
                'value': float(country_wines.aggregate(total=Sum('total_value_expr'))['total'] or 0),
            }

        by_vintage = {}
        vintages = wines.values_list('vintage', flat=True).distinct().order_by('-vintage')
        for vintage in vintages[:10]:
            vintage_wines = wines_with_total.filter(vintage=vintage)
            by_vintage[str(vintage)] = {
                'count': vintage_wines.aggregate(total=Sum('quantity'))['total'] or 0,
                'value': float(vintage_wines.aggregate(total=Sum('total_value_expr'))['total'] or 0),
            }

        top_wines = wines.order_by('-current_value')[:5]

        return Response({
            'total_bottles': total_bottles,
            'total_value': float(total_value),
            'total_cost': float(total_cost),
            'total_profit': float(total_value - total_cost),
            'appreciation_rate': float(appreciation_rate),
            'by_category': by_category,
            'by_country': by_country,
            'by_vintage': by_vintage,
            'top_wines': WineListSerializer(top_wines, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def valuation_trend(self, request):
        months = int(request.query_params.get('months', 12))
        all_valuations = ValuationHistory.objects.all().order_by('valuation_date')

        trend_data = []
        for v in all_valuations:
            trend_data.append({
                'date': v.valuation_date.isoformat(),
                'value': float(v.value),
                'wine': v.wine.name,
            })

        return Response(trend_data)

    @action(detail=False, methods=['get'])
    def maturity_distribution(self, request):
        wines = Wine.objects.all()
        distribution = {
            'cellared': 0,
            'drinking': 0,
            'peak': 0,
            'declining': 0,
        }
        for wine in wines:
            maturity = wine.get_current_maturity()
            distribution[maturity] = distribution.get(maturity, 0) + wine.quantity

        return Response(distribution)

    @action(detail=False, methods=['get'])
    def expiry_alerts(self, request):
        threshold_years = int(request.query_params.get('threshold', 1))
        wines = Wine.objects.exclude(status__in=['sold'])
        
        expiring_soon = []
        expired = []
        
        for wine in wines:
            expiry_status = wine.get_expiry_status(threshold_years)
            if expiry_status == 'expired':
                expired.append(wine)
            elif expiry_status == 'expiring_soon':
                expiring_soon.append(wine)
        
        return Response({
            'expiring_soon_count': sum(w.quantity for w in expiring_soon),
            'expired_count': sum(w.quantity for w in expired),
            'expiring_soon': WineListSerializer(expiring_soon, many=True).data,
            'expired': WineListSerializer(expired, many=True).data,
            'threshold_years': threshold_years
        })
