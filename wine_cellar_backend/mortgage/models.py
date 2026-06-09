from django.db import models
from django.utils import timezone
from decimal import Decimal


class MortgageApplication(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('reviewing', '审核中'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('active', '还款中'),
        ('completed', '已结清'),
        ('defaulted', '已违约'),
        ('liquidated', '已处置'),
    )

    applicant_name = models.CharField(max_length=100, verbose_name='申请人姓名')
    applicant_id = models.CharField(max_length=50, verbose_name='身份证号')
    applicant_phone = models.CharField(max_length=20, verbose_name='联系电话')
    applicant_email = models.EmailField(verbose_name='电子邮箱')

    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='申请贷款金额(元)')
    loan_term_months = models.IntegerField(verbose_name='贷款期限(月)')
    interest_rate = models.FloatField(verbose_name='年利率(%)')
    purpose = models.TextField(verbose_name='贷款用途')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    application_date = models.DateTimeField(auto_now_add=True, verbose_name='申请日期')
    review_date = models.DateTimeField(null=True, blank=True, verbose_name='审核日期')
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name='批准日期')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='放款日期')
    maturity_date = models.DateTimeField(null=True, blank=True, verbose_name='到期日期')

    approved_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='批准金额(元)')
    review_notes = models.TextField(blank=True, verbose_name='审核意见')
    collateral_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='抵押品估值(元)')
    ltv_ratio = models.FloatField(null=True, blank=True, verbose_name='抵押率(%)')

    total_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='已还金额(元)')
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='剩余金额(元)')

    class Meta:
        verbose_name = '抵押申请'
        verbose_name_plural = '抵押申请'
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.applicant_name} - {self.loan_amount}元"

    def save(self, *args, **kwargs):
        if self.approved_amount and self.collateral_value and self.collateral_value > 0:
            self.ltv_ratio = float(self.approved_amount / self.collateral_value * 100)
        if self.status == 'active' and not self.remaining_amount and self.approved_amount:
            self.remaining_amount = self.approved_amount
        super().save(*args, **kwargs)


class MortgageCollateral(models.Model):
    application = models.ForeignKey(MortgageApplication, related_name='collaterals', on_delete=models.CASCADE)
    wine = models.ForeignKey('collection.Wine', related_name='mortgages', on_delete=models.PROTECT)
    quantity = models.IntegerField(verbose_name='抵押数量(瓶)')
    unit_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='单价估值(元)')
    total_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总估值(元)')
    storage_location = models.CharField(max_length=100, verbose_name='存放位置')
    insurance_policy = models.CharField(max_length=100, blank=True, verbose_name='保单号')
    appraisal_report = models.TextField(blank=True, verbose_name='评估报告')
    released = models.BooleanField(default=False, verbose_name='是否已解押')
    released_date = models.DateTimeField(null=True, blank=True, verbose_name='解押日期')

    class Meta:
        verbose_name = '抵押品'
        verbose_name_plural = '抵押品'

    def __str__(self):
        return f"{self.wine.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_value = self.unit_value * self.quantity
        super().save(*args, **kwargs)


class RepaymentSchedule(models.Model):
    application = models.ForeignKey(MortgageApplication, related_name='schedules', on_delete=models.CASCADE)
    payment_number = models.IntegerField(verbose_name='期数')
    due_date = models.DateField(verbose_name='还款日')
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='应还本金(元)')
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='应还利息(元)')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='应还总额(元)')
    paid = models.BooleanField(default=False, verbose_name='是否已还')
    paid_date = models.DateField(null=True, blank=True, verbose_name='实际还款日期')
    late_days = models.IntegerField(default=0, verbose_name='逾期天数')
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='罚息(元)')

    class Meta:
        verbose_name = '还款计划'
        verbose_name_plural = '还款计划'
        ordering = ['payment_number']

    def __str__(self):
        return f"{self.application} - 第{self.payment_number}期"


class RepaymentRecord(models.Model):
    PAYMENT_METHODS = (
        ('bank_transfer', '银行转账'),
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('cash', '现金'),
        ('other', '其他'),
    )

    schedule = models.ForeignKey(RepaymentSchedule, related_name='records', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='还款金额(元)')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='还款方式')
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name='交易流水号')
    payment_date = models.DateTimeField(default=timezone.now, verbose_name='还款日期')
    notes = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '还款记录'
        verbose_name_plural = '还款记录'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.schedule} - {self.amount}元"
