from django.db import models
from django.utils import timezone
from decimal import Decimal


class Customer(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    )
    LEVEL_CHOICES = (
        ('normal', '普通客户'),
        ('silver', '银卡会员'),
        ('gold', '金卡会员'),
        ('platinum', '白金会员'),
        ('diamond', '钻石会员'),
    )

    name = models.CharField(max_length=100, verbose_name='客户姓名')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='性别')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    email = models.EmailField(blank=True, verbose_name='电子邮箱')
    id_card = models.CharField(max_length=50, blank=True, verbose_name='身份证号')
    address = models.CharField(max_length=300, blank=True, verbose_name='联系地址')

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='normal', verbose_name='会员等级')
    total_purchases = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='累计消费金额(元)')
    total_orders = models.IntegerField(default=0, verbose_name='订单总数')

    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '客户档案'
        verbose_name_plural = '客户档案'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SaleOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('returned', '已退货'),
    )
    PAYMENT_METHODS = (
        ('bank_transfer', '银行转账'),
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('cash', '现金'),
        ('credit_card', '信用卡'),
        ('other', '其他'),
    )

    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.PROTECT, verbose_name='客户')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='订单状态')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, verbose_name='支付方式')

    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='商品小计(元)')
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='折扣金额(元)')
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='运费(元)')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='订单总额(元)')

    order_date = models.DateTimeField(default=timezone.now, verbose_name='下单时间')
    confirmed_date = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    shipped_date = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    shipping_address = models.CharField(max_length=300, blank=True, verbose_name='收货地址')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='物流单号')
    notes = models.TextField(blank=True, verbose_name='备注')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '售出订单'
        verbose_name_plural = '售出订单'
        ordering = ['-order_date']

    def __str__(self):
        return self.order_no

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f'SO{timezone.now().strftime("%Y%m%d%H%M%S")}'
        self.total_amount = self.subtotal - self.discount + self.shipping_fee
        super().save(*args, **kwargs)

    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.total_amount = self.subtotal - self.discount + self.shipping_fee
        self.save()

    def confirm_order(self):
        if self.status == 'draft':
            for item in self.items.all():
                wine = item.wine
                if wine.quantity < item.quantity:
                    raise ValueError(f'酒品 {wine.name} 库存不足，当前库存: {wine.quantity}瓶')
                wine.quantity -= item.quantity
                if wine.quantity == 0:
                    wine.status = 'sold'
                wine.save()
            self.status = 'confirmed'
            self.confirmed_date = timezone.now()
            self.save()
            self.customer.total_orders += 1
            self.customer.total_purchases += self.total_amount
            self._update_customer_level()
            self.customer.save()

    def cancel_order(self):
        if self.status == 'confirmed':
            for item in self.items.all():
                wine = item.wine
                wine.quantity += item.quantity
                if wine.status == 'sold' and wine.quantity > 0:
                    wine.status = 'cellared'
                wine.save()
            self.status = 'cancelled'
            self.save()
            self.customer.total_orders -= 1
            self.customer.total_purchases -= self.total_amount
            self._update_customer_level()
            self.customer.save()

    def _update_customer_level(self):
        total = float(self.customer.total_purchases)
        if total >= 500000:
            self.customer.level = 'diamond'
        elif total >= 200000:
            self.customer.level = 'platinum'
        elif total >= 100000:
            self.customer.level = 'gold'
        elif total >= 50000:
            self.customer.level = 'silver'
        else:
            self.customer.level = 'normal'


class SaleOrderItem(models.Model):
    order = models.ForeignKey(SaleOrder, related_name='items', on_delete=models.CASCADE, verbose_name='订单')
    wine = models.ForeignKey('collection.Wine', related_name='sale_items', on_delete=models.PROTECT, verbose_name='酒品')
    quantity = models.IntegerField(verbose_name='数量(瓶)')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='单价(元)')
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='总价(元)')
    notes = models.CharField(max_length=200, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '订单明细'
        verbose_name_plural = '订单明细'

    def __str__(self):
        return f"{self.order.order_no} - {self.wine.name}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class AuctionRecord(models.Model):
    STATUS_CHOICES = (
        ('upcoming', '即将开拍'),
        ('ongoing', '拍卖中'),
        ('ended', '已结束'),
        ('cancelled', '已取消'),
    )

    title = models.CharField(max_length=200, verbose_name='拍卖标题')
    wine = models.ForeignKey('collection.Wine', related_name='auctions', on_delete=models.PROTECT, verbose_name='酒品')
    quantity = models.IntegerField(verbose_name='拍卖数量(瓶)')

    start_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='起拍价(元)')
    reserve_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='保留价(元)')
    current_bid = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='当前出价(元)')
    final_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='成交价(元)')

    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='状态')
    winner = models.ForeignKey(Customer, related_name='auctions_won', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='中标客户')
    bid_count = models.IntegerField(default=0, verbose_name='出价次数')

    auction_house = models.CharField(max_length=200, blank=True, verbose_name='拍卖行')
    lot_number = models.CharField(max_length=50, blank=True, verbose_name='拍品编号')
    notes = models.TextField(blank=True, verbose_name='备注')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '拍卖记录'
        verbose_name_plural = '拍卖记录'
        ordering = ['-start_time']

    def __str__(self):
        return self.title

    def place_bid(self, customer, amount):
        if self.status != 'ongoing':
            raise ValueError('拍卖不在进行中')
        if self.current_bid and amount <= self.current_bid:
            raise ValueError('出价必须高于当前出价')
        if amount < self.start_price:
            raise ValueError('出价不得低于起拍价')
        self.current_bid = amount
        self.bid_count += 1
        self.winner = customer
        self.save()

    def end_auction(self):
        if self.status != 'ongoing':
            raise ValueError('拍卖不在进行中')
        if self.current_bid and self.current_bid >= self.reserve_price:
            self.final_price = self.current_bid
            self.status = 'ended'
            wine = self.wine
            wine.quantity -= self.quantity
            if wine.quantity <= 0:
                wine.status = 'sold'
            wine.save()
            if self.winner:
                self.winner.total_purchases += self.final_price
                self.winner.total_orders += 1
                self.winner.save()
        else:
            self.status = 'ended'
        self.save()


class AuctionBid(models.Model):
    auction = models.ForeignKey(AuctionRecord, related_name='bids', on_delete=models.CASCADE, verbose_name='拍卖')
    bidder = models.ForeignKey(Customer, related_name='bids', on_delete=models.CASCADE, verbose_name='出价人')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='出价金额(元)')
    bid_time = models.DateTimeField(default=timezone.now, verbose_name='出价时间')

    class Meta:
        verbose_name = '拍卖出价'
        verbose_name_plural = '拍卖出价'
        ordering = ['-bid_time']

    def __str__(self):
        return f"{self.auction.title} - {self.bidder.name} - {self.amount}"
