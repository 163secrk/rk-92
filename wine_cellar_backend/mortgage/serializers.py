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
    class Meta:
        model = MortgageApplication
        fields = ['applicant_name', 'applicant_id', 'applicant_phone', 'applicant_email',
                  'loan_amount', 'loan_term_months', 'interest_rate', 'purpose']
