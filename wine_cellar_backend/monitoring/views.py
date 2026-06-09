from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from .models import WineCellar, SensorReading, Alert
from .serializers import WineCellarSerializer, SensorReadingSerializer, AlertSerializer
import random


class WineCellarViewSet(viewsets.ModelViewSet):
    queryset = WineCellar.objects.all()
    serializer_class = WineCellarSerializer

    @action(detail=True, methods=['get'])
    def current_status(self, request, pk=None):
        cellar = self.get_object()
        latest = cellar.readings.first()
        return Response({
            'cellar': WineCellarSerializer(cellar).data,
            'latest_reading': SensorReadingSerializer(latest).data if latest else None,
            'active_alerts': AlertSerializer(cellar.alerts.filter(status='active'), many=True).data,
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        cellar = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        readings = cellar.readings.filter(timestamp__gte=start_time).order_by('timestamp')

        data = []
        for r in readings:
            data.append({
                'timestamp': r.timestamp.isoformat(),
                'temperature': r.temperature,
                'humidity': r.humidity,
            })

        return Response(data)

    @action(detail=True, methods=['post'])
    def simulate_reading(self, request, pk=None):
        cellar = self.get_object()
        base_temp = (cellar.optimal_temp_min + cellar.optimal_temp_max) / 2
        base_humidity = (cellar.optimal_humidity_min + cellar.optimal_humidity_max) / 2

        temp_variation = random.uniform(-2, 2)
        humidity_variation = random.uniform(-5, 5)

        reading = SensorReading.objects.create(
            cellar=cellar,
            temperature=round(base_temp + temp_variation, 1),
            humidity=round(base_humidity + humidity_variation, 1),
        )

        if reading.temperature > cellar.optimal_temp_max + 0.5:
            Alert.objects.create(
                cellar=cellar,
                alert_type='temp_high',
                severity='warning' if reading.temperature < cellar.optimal_temp_max + 2 else 'critical',
                reading=reading,
                value=reading.temperature,
                message=f'温度过高: {reading.temperature}°C'
            )
        elif reading.temperature < cellar.optimal_temp_min - 0.5:
            Alert.objects.create(
                cellar=cellar,
                alert_type='temp_low',
                severity='warning' if reading.temperature > cellar.optimal_temp_min - 2 else 'critical',
                reading=reading,
                value=reading.temperature,
                message=f'温度过低: {reading.temperature}°C'
            )

        if reading.humidity > cellar.optimal_humidity_max + 2:
            Alert.objects.create(
                cellar=cellar,
                alert_type='humidity_high',
                severity='warning' if reading.humidity < cellar.optimal_humidity_max + 5 else 'critical',
                reading=reading,
                value=reading.humidity,
                message=f'湿度过高: {reading.humidity}%'
            )
        elif reading.humidity < cellar.optimal_humidity_min - 2:
            Alert.objects.create(
                cellar=cellar,
                alert_type='humidity_low',
                severity='warning' if reading.humidity > cellar.optimal_humidity_min - 5 else 'critical',
                reading=reading,
                value=reading.humidity,
                message=f'湿度过低: {reading.humidity}%'
            )

        return Response(SensorReadingSerializer(reading).data)


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        return Response(AlertSerializer(alert).data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        alerts = Alert.objects.filter(status='active').order_by('-created_at')
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        active_count = Alert.objects.filter(status='active').count()
        warning_count = Alert.objects.filter(status='active', severity='warning').count()
        critical_count = Alert.objects.filter(status='active', severity='critical').count()
        return Response({
            'active': active_count,
            'warning': warning_count,
            'critical': critical_count,
        })
