from django.db import models
from django.utils import timezone


class WineCellar(models.Model):
    name = models.CharField(max_length=100, verbose_name='酒窖名称')
    location = models.CharField(max_length=200, verbose_name='位置')
    capacity = models.IntegerField(verbose_name='容量(瓶)')
    optimal_temp_min = models.FloatField(default=10.0, verbose_name='最佳温度下限(°C)')
    optimal_temp_max = models.FloatField(default=15.0, verbose_name='最佳温度上限(°C)')
    optimal_humidity_min = models.FloatField(default=60.0, verbose_name='最佳湿度下限(%)')
    optimal_humidity_max = models.FloatField(default=80.0, verbose_name='最佳湿度上限(%)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '酒窖'
        verbose_name_plural = '酒窖'

    def __str__(self):
        return self.name

    def get_current_status(self):
        latest = self.readings.order_by('-timestamp').first()
        if not latest:
            return 'unknown'
        temp_ok = self.optimal_temp_min <= latest.temperature <= self.optimal_temp_max
        humidity_ok = self.optimal_humidity_min <= latest.humidity <= self.optimal_humidity_max
        if temp_ok and humidity_ok:
            return 'normal'
        elif not temp_ok and not humidity_ok:
            return 'critical'
        else:
            return 'warning'


class SensorReading(models.Model):
    cellar = models.ForeignKey(WineCellar, related_name='readings', on_delete=models.CASCADE)
    temperature = models.FloatField(verbose_name='温度(°C)')
    humidity = models.FloatField(verbose_name='湿度(%)')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = '传感器读数'
        verbose_name_plural = '传感器读数'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.cellar.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def get_temp_status(self):
        temp_ok = self.cellar.optimal_temp_min <= self.temperature <= self.cellar.optimal_temp_max
        return 'normal' if temp_ok else 'alert'

    def get_humidity_status(self):
        humidity_ok = self.cellar.optimal_humidity_min <= self.humidity <= self.cellar.optimal_humidity_max
        return 'normal' if humidity_ok else 'alert'


class Alert(models.Model):
    ALERT_TYPES = (
        ('temp_high', '温度过高'),
        ('temp_low', '温度过低'),
        ('humidity_high', '湿度过高'),
        ('humidity_low', '湿度过低'),
    )
    SEVERITY_CHOICES = (
        ('warning', '警告'),
        ('critical', '严重'),
    )
    STATUS_CHOICES = (
        ('active', '未处理'),
        ('acknowledged', '已确认'),
        ('resolved', '已解决'),
    )

    cellar = models.ForeignKey(WineCellar, related_name='alerts', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    reading = models.ForeignKey(SensorReading, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.FloatField(verbose_name='当前值')
    message = models.TextField(verbose_name='告警消息')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '告警'
        verbose_name_plural = '告警'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.cellar.name} - {self.get_alert_type_display()}"
