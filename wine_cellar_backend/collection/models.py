from django.db import models
from django.utils import timezone


class Wine(models.Model):
    CATEGORY_CHOICES = (
        ('red', '红葡萄酒'),
        ('white', '白葡萄酒'),
        ('rose', '桃红葡萄酒'),
        ('sparkling', '起泡酒'),
        ('dessert', '甜酒'),
        ('fortified', '加强酒'),
    )
    STATUS_CHOICES = (
        ('cellared', '窖藏中'),
        ('drinking', '适饮期'),
        ('peak', '巅峰期'),
        ('declining', '衰退期'),
        ('sold', '已售出'),
        ('mortgaged', '已抵押'),
    )

    name = models.CharField(max_length=200, verbose_name='酒品名称')
    chateau = models.CharField(max_length=200, verbose_name='酒庄')
    region = models.CharField(max_length=100, verbose_name='产区')
    country = models.CharField(max_length=50, verbose_name='国家')
    vintage = models.IntegerField(verbose_name='年份')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='类型')
    grape_variety = models.CharField(max_length=200, verbose_name='葡萄品种')
    alcohol_content = models.FloatField(verbose_name='酒精度(%)')
    bottle_size = models.FloatField(default=0.75, verbose_name='容量(L)')
    quantity = models.IntegerField(default=1, verbose_name='数量(瓶)')

    purchase_date = models.DateField(verbose_name='购买日期')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='购买价格(元)')
    current_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='当前估值(元)')
    last_valuation_date = models.DateField(auto_now=True, verbose_name='最近估值日期')

    cellar_location = models.CharField(max_length=50, verbose_name='酒窖位置')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cellared', verbose_name='状态')
    drinking_window_start = models.IntegerField(verbose_name='适饮期开始年份')
    drinking_window_end = models.IntegerField(verbose_name='适饮期结束年份')

    tasting_notes = models.TextField(blank=True, verbose_name='品鉴笔记')
    storage_notes = models.TextField(blank=True, verbose_name='存储笔记')
    image_url = models.URLField(blank=True, verbose_name='图片链接')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '酒品'
        verbose_name_plural = '酒品'
        ordering = ['-current_value']

    def __str__(self):
        return f"{self.name} {self.vintage}"

    def appreciation_rate(self):
        if self.purchase_price == 0:
            return 0
        return ((self.current_value - self.purchase_price) / self.purchase_price) * 100

    def total_value(self):
        return self.current_value * self.quantity

    def total_cost(self):
        return self.purchase_price * self.quantity

    def total_profit(self):
        return (self.current_value - self.purchase_price) * self.quantity

    def get_current_maturity(self):
        current_year = timezone.now().year
        if current_year < self.drinking_window_start:
            return 'cellared'
        mid_point = (self.drinking_window_start + self.drinking_window_end) // 2
        if abs(current_year - mid_point) <= 2:
            return 'peak'
        if current_year <= self.drinking_window_end:
            return 'drinking'
        return 'declining'


class ValuationHistory(models.Model):
    wine = models.ForeignKey(Wine, related_name='valuations', on_delete=models.CASCADE)
    valuation_date = models.DateField(default=timezone.now)
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='估值(元)')
    change_percent = models.FloatField(verbose_name='变化率(%)')
    reason = models.CharField(max_length=200, verbose_name='估值原因')
    notes = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '估值历史'
        verbose_name_plural = '估值历史'
        ordering = ['-valuation_date']

    def __str__(self):
        return f"{self.wine.name} - {self.valuation_date}"


class CollectionStats(models.Model):
    total_bottles = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_appreciation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    appreciation_rate = models.FloatField(default=0)
    by_category = models.JSONField(default=dict)
    by_country = models.JSONField(default=dict)
    by_vintage = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '收藏统计'
        verbose_name_plural = '收藏统计'
        ordering = ['-calculated_at']
