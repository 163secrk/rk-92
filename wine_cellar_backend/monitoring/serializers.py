from rest_framework import serializers
from .models import WineCellar, SensorReading, Alert


class WineCellarSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField()
    current_temp = serializers.SerializerMethodField()
    current_humidity = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()

    class Meta:
        model = WineCellar
        fields = '__all__'

    def get_current_status(self, obj):
        return obj.get_current_status()

    def get_current_temp(self, obj):
        latest = obj.readings.first()
        return latest.temperature if latest else None

    def get_current_humidity(self, obj):
        latest = obj.readings.first()
        return latest.humidity if latest else None

    def get_alert_count(self, obj):
        return obj.alerts.filter(status='active').count()


class SensorReadingSerializer(serializers.ModelSerializer):
    temp_status = serializers.SerializerMethodField()
    humidity_status = serializers.SerializerMethodField()

    class Meta:
        model = SensorReading
        fields = '__all__'

    def get_temp_status(self, obj):
        return obj.get_temp_status()

    def get_humidity_status(self, obj):
        return obj.get_humidity_status()


class AlertSerializer(serializers.ModelSerializer):
    cellar_name = serializers.CharField(source='cellar.name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'
