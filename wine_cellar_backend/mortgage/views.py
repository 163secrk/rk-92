from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, timedelta
from .models import MortgageApplication, MortgageCollateral, RepaymentSchedule, RepaymentRecord
from .serializers import (
    MortgageApplicationSerializer, MortgageApplicationListSerializer,
    MortgageApplicationCreateSerializer, MortgageCollateralSerializer,
    RepaymentScheduleSerializer, RepaymentRecordSerializer
)


class MortgageApplicationViewSet(viewsets.ModelViewSet):
    queryset = MortgageApplication.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return MortgageApplicationListSerializer
        elif self.action == 'create':
            return MortgageApplicationCreateSerializer
        return MortgageApplicationSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        app = self.get_object()
        if app.status != 'draft':
            return Response(
                {'detail': f'提交失败：申请状态不正确，当前状态为「{app.get_status_display()}」，仅「草稿」状态才能提交'},
                status=status.HTTP_400_BAD_REQUEST
            )
        app.status = 'submitted'
        app.save()
        return Response(MortgageApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        app = self.get_object()
        if app.status != 'submitted':
            return Response(
                {'detail': f'开始审核失败：申请状态不正确，当前状态为「{app.get_status_display()}」，仅「已提交」状态才能开始审核'},
                status=status.HTTP_400_BAD_REQUEST
            )
        app.status = 'reviewing'
        app.review_date = timezone.now()
        app.save()
        return Response(MortgageApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        app = self.get_object()

        if app.status != 'reviewing':
            return Response(
                {'detail': f'审批失败：申请状态不正确，当前状态为「{app.get_status_display()}」，仅「审核中」状态才能审批'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approved_amount = Decimal(request.data.get('approved_amount', app.loan_amount))
        review_notes = request.data.get('review_notes', '')

        if approved_amount <= 0:
            return Response(
                {'detail': '审批失败：批准金额必须大于0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_loan_amount = Decimal('10000000')
        if approved_amount > max_loan_amount:
            return Response(
                {'detail': f'审批失败：批准金额超限（当前{approved_amount}元），单笔贷款最高为1000万元'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collaterals = app.collaterals.all()
        if not collaterals.exists():
            return Response(
                {'detail': '审批失败：未添加抵押品，请先添加抵押品后再批准'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collateral_value = sum(c.total_value for c in collaterals)
        if collateral_value <= 0:
            return Response(
                {'detail': '审批失败：抵押品估值无效'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ltv_ratio = float(approved_amount / collateral_value * 100)
        if ltv_ratio > 70:
            return Response(
                {'detail': f'审批失败：抵押率过高（当前{ltv_ratio:.1f}%），最高不得超过70%。请降低批准金额或要求申请人增加抵押品。'},
                status=status.HTTP_400_BAD_REQUEST
            )

        app.status = 'approved'
        app.approved_amount = approved_amount
        app.review_notes = review_notes
        app.collateral_value = collateral_value
        app.approval_date = timezone.now()
        app.save()

        for c in collaterals:
            c.wine.status = 'mortgaged'
            c.wine.save()

        return Response(MortgageApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        app = self.get_object()
        if app.status != 'reviewing':
            return Response(
                {'detail': f'拒绝失败：申请状态不正确，当前状态为「{app.get_status_display()}」，仅「审核中」状态才能拒绝'},
                status=status.HTTP_400_BAD_REQUEST
            )
        app.status = 'rejected'
        app.review_notes = request.data.get('review_notes', '')
        app.review_date = timezone.now()
        app.save()
        return Response(MortgageApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        app = self.get_object()

        if app.status != 'approved':
            return Response(
                {'detail': f'放款失败：申请状态不正确，当前状态为「{app.get_status_display()}」，仅「已批准」状态才能放款'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not app.approved_amount or app.approved_amount <= 0:
            return Response(
                {'detail': '放款失败：批准金额无效，请先完成审核'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collaterals = app.collaterals.all()
        if not collaterals.exists():
            return Response(
                {'detail': '放款失败：未添加抵押品，请先添加抵押品'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collateral_value = sum(c.total_value for c in collaterals)
        if collateral_value <= 0:
            return Response(
                {'detail': '放款失败：抵押品估值无效'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ltv_ratio = float(app.approved_amount / collateral_value * 100)
        if ltv_ratio > 70:
            return Response(
                {'detail': f'放款失败：抵押率过高（当前{ltv_ratio:.1f}%），最高不得超过70%。请减少贷款金额或增加抵押品。'},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_loan_amount = Decimal('10000000')
        if app.approved_amount > max_loan_amount:
            return Response(
                {'detail': f'放款失败：贷款金额超限（当前{app.approved_amount}元），单笔贷款最高为1000万元'},
                status=status.HTTP_400_BAD_REQUEST
            )

        app.status = 'active'
        app.start_date = timezone.now()
        app.maturity_date = timezone.now() + timedelta(days=30 * app.loan_term_months)
        app.remaining_amount = app.approved_amount
        app.save()

        principal = app.approved_amount
        rate = app.interest_rate / 100 / 12
        n = app.loan_term_months

        monthly_payment = principal * rate * (1 + rate)**n / ((1 + rate)**n - 1)

        remaining = principal
        for i in range(1, n + 1):
            interest = remaining * rate
            principal_payment = monthly_payment - interest
            remaining -= principal_payment
            due_date = timezone.now() + timedelta(days=30 * i)

            RepaymentSchedule.objects.create(
                application=app,
                payment_number=i,
                due_date=due_date,
                principal_amount=principal_payment,
                interest_amount=interest,
                total_amount=monthly_payment,
            )

        return Response(MortgageApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def add_collateral(self, request, pk=None):
        app = self.get_object()
        from collection.models import Wine
        wine_id = request.data.get('wine_id')
        quantity = int(request.data.get('quantity', 1))

        wine = Wine.objects.get(id=wine_id)
        unit_value = wine.current_value

        collateral = MortgageCollateral.objects.create(
            application=app,
            wine=wine,
            quantity=quantity,
            unit_value=unit_value,
            total_value=unit_value * quantity,
            storage_location=wine.cellar_location,
        )

        return Response(MortgageCollateralSerializer(collateral).data)

    @action(detail=True, methods=['post'])
    def remove_collateral(self, request, pk=None):
        collateral_id = request.data.get('collateral_id')
        collateral = MortgageCollateral.objects.get(id=collateral_id)
        collateral.delete()
        return Response({'status': 'success'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_applications = MortgageApplication.objects.count()
        active_loans = MortgageApplication.objects.filter(status='active')
        total_loan_amount = active_loans.aggregate(total=Sum('approved_amount'))['total'] or 0
        total_remaining = active_loans.aggregate(total=Sum('remaining_amount'))['total'] or 0

        status_counts = {}
        for status_code, _ in MortgageApplication.STATUS_CHOICES:
            status_counts[status_code] = MortgageApplication.objects.filter(status=status_code).count()

        return Response({
            'total_applications': total_applications,
            'active_loans': active_loans.count(),
            'total_loan_amount': float(total_loan_amount),
            'total_remaining': float(total_remaining),
            'status_counts': status_counts,
        })


class MortgageCollateralViewSet(viewsets.ModelViewSet):
    queryset = MortgageCollateral.objects.all()
    serializer_class = MortgageCollateralSerializer

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        collateral = self.get_object()
        collateral.released = True
        collateral.released_date = timezone.now()
        collateral.save()

        if collateral.wine.status == 'mortgaged':
            collateral.wine.status = 'cellared'
            collateral.wine.save()

        return Response(MortgageCollateralSerializer(collateral).data)


class RepaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = RepaymentSchedule.objects.all()
    serializer_class = RepaymentScheduleSerializer

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        schedule = self.get_object()
        amount = Decimal(request.data.get('amount', schedule.total_amount))
        payment_method = request.data.get('payment_method', 'bank_transfer')
        transaction_id = request.data.get('transaction_id', '')

        record = RepaymentRecord.objects.create(
            schedule=schedule,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
        )

        schedule.paid = True
        schedule.paid_date = timezone.now()
        schedule.save()

        app = schedule.application
        app.total_paid += amount
        app.remaining_amount -= amount
        if app.remaining_amount <= 0:
            app.status = 'completed'
            for c in app.collaterals.all():
                c.released = True
                c.released_date = timezone.now()
                c.save()
                if c.wine.status == 'mortgaged':
                    c.wine.status = 'cellared'
                    c.wine.save()
        app.save()

        return Response({
            'record': RepaymentRecordSerializer(record).data,
            'schedule': RepaymentScheduleSerializer(schedule).data,
        })


class RepaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = RepaymentRecord.objects.all()
    serializer_class = RepaymentRecordSerializer
