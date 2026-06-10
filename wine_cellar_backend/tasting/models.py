from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from collection.models import Wine

User = get_user_model()


class TastingEvent(models.Model):
    STATUS_CHOICES = (
        ('upcoming', '待开始'),
        ('ongoing', '进行中'),
        ('completed', '已结束'),
        ('cancelled', '已取消'),
    )

    name = models.CharField(max_length=200, verbose_name='品鉴会名称')
    theme = models.CharField(max_length=200, verbose_name='主题')
    description = models.TextField(blank=True, verbose_name='描述')
    event_date = models.DateTimeField(verbose_name='活动时间')
    location = models.CharField(max_length=200, verbose_name='地点')
    organizer = models.CharField(max_length=100, verbose_name='主办方')
    max_attendees = models.IntegerField(default=20, verbose_name='最大人数')
    wines = models.ManyToManyField(Wine, related_name='tasting_events', blank=True, verbose_name='品鉴酒品')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='状态')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tastings', verbose_name='创建人')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '品鉴会'
        verbose_name_plural = '品鉴会'
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.name} - {self.event_date.strftime('%Y-%m-%d')}"

    def get_status_display_cn(self):
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, '未知')

    def get_current_status(self):
        now = timezone.now()
        if self.status == 'cancelled':
            return 'cancelled'
        if now < self.event_date:
            return 'upcoming'
        event_end = self.event_date + timezone.timedelta(hours=3)
        if now <= event_end:
            return 'ongoing'
        return 'completed'

    def update_status_based_on_time(self):
        self.status = self.get_current_status()
        self.save(update_fields=['status'])

    def checked_in_count(self):
        return self.attendees.filter(checked_in=True).count()

    def registered_count(self):
        return self.attendees.count()

    def average_rating(self):
        notes = self.tasting_notes.all()
        if not notes:
            return 0
        total = sum(n.overall_rating for n in notes if n.overall_rating)
        return round(total / len(notes), 1)


class TastingAttendee(models.Model):
    event = models.ForeignKey(TastingEvent, related_name='attendees', on_delete=models.CASCADE, verbose_name='品鉴会')
    name = models.CharField(max_length=100, verbose_name='姓名')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    company = models.CharField(max_length=100, blank=True, verbose_name='公司')
    position = models.CharField(max_length=50, blank=True, verbose_name='职位')
    checked_in = models.BooleanField(default=False, verbose_name='已签到')
    check_in_time = models.DateTimeField(null=True, blank=True, verbose_name='签到时间')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '签到人员'
        verbose_name_plural = '签到人员'
        ordering = ['-created_at']
        unique_together = ['event', 'phone']

    def __str__(self):
        return f"{self.name} - {self.event.name}"

    def do_check_in(self):
        if not self.checked_in:
            self.checked_in = True
            self.check_in_time = timezone.now()
            self.save(update_fields=['checked_in', 'check_in_time'])


class TastingNote(models.Model):
    event = models.ForeignKey(TastingEvent, related_name='tasting_notes', on_delete=models.CASCADE, verbose_name='品鉴会')
    wine = models.ForeignKey(Wine, related_name='tasting_records', on_delete=models.CASCADE, verbose_name='酒品')
    attendee = models.ForeignKey(TastingAttendee, related_name='tasting_notes', on_delete=models.CASCADE, verbose_name='品鉴人')

    color_rating = models.IntegerField(verbose_name='颜色评分', help_text='1-5分')
    aroma_rating = models.IntegerField(verbose_name='香气评分', help_text='1-5分')
    taste_rating = models.IntegerField(verbose_name='口感评分', help_text='1-5分')
    finish_rating = models.IntegerField(verbose_name='余味评分', help_text='1-5分')
    overall_rating = models.FloatField(verbose_name='综合评分', editable=False)

    color_notes = models.TextField(blank=True, verbose_name='颜色描述')
    aroma_notes = models.TextField(blank=True, verbose_name='香气描述')
    taste_notes = models.TextField(blank=True, verbose_name='口感描述')
    finish_notes = models.TextField(blank=True, verbose_name='余味描述')
    general_notes = models.TextField(blank=True, verbose_name='综合评价')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '品鉴笔记'
        verbose_name_plural = '品鉴笔记'
        ordering = ['-created_at']
        unique_together = ['event', 'wine', 'attendee']

    def __str__(self):
        return f"{self.attendee.name} - {self.wine.name}"

    def save(self, *args, **kwargs):
        ratings = [self.color_rating, self.aroma_rating, self.taste_rating, self.finish_rating]
        self.overall_rating = round(sum(ratings) / len(ratings), 1)
        super().save(*args, **kwargs)
