from rest_framework import serializers
from .models import MortgageApplication, MortgageCollateral, RepaymentSchedule, RepaymentRecord


class MortgageCollateralSerializer(serializers.ModelSerializer):
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)
    wine_chateau = serializers.CharField(source='wine.chateau', read_only=True)

    class Meta:
        model = MortgageCollateral
        fields = '__all__'


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = '__all__'


class RepaymentRecordSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = RepaymentRecord
        fields = '__all__'


class MortgageApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    collaterals = MortgageCollateralSerializer(many=True, read_only=True)
    schedules = RepaymentScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = MortgageApplication
        fields = '__all__'


class MortgageApplicationListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    collateral_count = serializers.SerializerMethodField()

    class Meta:
        model = MortgageApplication
        fields = ['id', 'applicant_name', 'applicant_phone', 'loan_amount',
                  'approved_amount', 'loan_term_months', 'interest_rate',
                  'status', 'status_display', 'application_date', 'collateral_count',
                  'collateral_value', 'ltv_ratio', 'total_paid', 'remaining_amount']

    def get_collateral_count(self, obj):
        return obj.collaterals.count()


class MortgageApplicationCreateSerializer(serializers.ModelSerializer):
    def validate_applicant_phone(self, value):
        import re
        phone_reg = r'^1[3-9]\d{9}$'
        if not re.match(phone_reg, value):
            raise serializers.ValidationError('请输入正确的11位手机号码')
        return value

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('贷款金额必须大于0')
        if value < 1000:
            raise serializers.ValidationError('贷款金额不能低于1000元')
        if value > 10000000:
            raise serializers.ValidationError('贷款金额不能超过1000万元')
        return value

    def validate_applicant_id(self, value):
        import re
        id_reg = r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)'
        if not re.match(id_reg, value):
            raise serializers.ValidationError('请输入正确的身份证号')
        return value

    def validate(self, attrs):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(attrs.get('applicant_email', ''))
        except ValidationError:
            raise serializers.ValidationError({'applicant_email': '请输入正确的邮箱格式'})
        return attrs

    class Meta:
        model = MortgageApplication
        fields = ['applicant_name', 'applicant_id', 'applicant_phone', 'applicant_email',
                  'loan_amount', 'loan_term_months', 'interest_rate', 'purpose']
