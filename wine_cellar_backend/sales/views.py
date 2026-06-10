from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import Customer, SaleOrder, SaleOrderItem, AuctionRecord, AuctionBid
from .serializers import (
    CustomerSerializer, CustomerListSerializer,
    SaleOrderSerializer, SaleOrderListSerializer, SaleOrderCreateSerializer,
    SaleOrderItemSerializer,
    AuctionRecordSerializer, AuctionRecordListSerializer,
    AuctionBidSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.all()
        level = self.request.query_params.get('level')
        keyword = self.request.query_params.get('q')
        if level:
            queryset = queryset.filter(level=level)
        if keyword:
            queryset = queryset.filter(name__icontains=keyword) | \
                       queryset.filter(phone__icontains=keyword)
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('q', '')
        queryset = Customer.objects.filter(name__icontains=keyword) | \
                   Customer.objects.filter(phone__icontains=keyword)
        return Response(CustomerListSerializer(queryset[:20], many=True).data)


class SaleOrderViewSet(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleOrderListSerializer
        elif self.action == 'create':
            return SaleOrderCreateSerializer
        return SaleOrderSerializer

    def get_queryset(self):
        queryset = SaleOrder.objects.all()
        status_param = self.request.query_params.get('status')
        customer = self.request.query_params.get('customer')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if customer:
            queryset = queryset.filter(customer_id=customer)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        order = SaleOrder.objects.get(pk=serializer.instance.pk)
        return Response(SaleOrderSerializer(order).data,
                        status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            order.confirm_order()
            return Response(SaleOrderSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        try:
            order.cancel_order()
            return Response(SaleOrderSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status != 'confirmed':
            return Response({'error': '只有已确认的订单才能发货'},
                            status=status.HTTP_400_BAD_REQUEST)
        order.status = 'shipped'
        order.shipped_date = timezone.now()
        tracking_number = request.data.get('tracking_number')
        if tracking_number:
            order.tracking_number = tracking_number
        order.save()
        return Response(SaleOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['shipped', 'confirmed']:
            return Response({'error': '只有已发货或已确认的订单才能完成'},
                            status=status.HTTP_400_BAD_REQUEST)
        order.status = 'completed'
        order.completed_date = timezone.now()
        order.save()
        return Response(SaleOrderSerializer(order).data)

    @action(detail=True, methods=['get', 'post'])
    def items(self, request, pk=None):
        order = self.get_object()
        if request.method == 'GET':
            items = order.items.all()
            return Response(SaleOrderItemSerializer(items, many=True).data)
        else:
            if order.status != 'draft':
                return Response({'error': '只有草稿状态的订单才能添加商品'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SaleOrderItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(order=order)
            order.calculate_totals()
            return Response(SaleOrderItemSerializer(item).data,
                            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'delete'], url_path='items/(?P<item_id>[^/.]+)')
    def item_detail(self, request, pk=None, item_id=None):
        order = self.get_object()
        try:
            item = order.items.get(pk=item_id)
        except SaleOrderItem.DoesNotExist:
            return Response({'error': '订单项不存在'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'draft':
            return Response({'error': '只有草稿状态的订单才能修改商品'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'PUT':
            serializer = SaleOrderItemSerializer(item, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            order.calculate_totals()
            return Response(SaleOrderItemSerializer(item).data)
        else:
            item.delete()
            order.calculate_totals()
            return Response(status=status.HTTP_204_NO_CONTENT)


class AuctionRecordViewSet(viewsets.ModelViewSet):
    queryset = AuctionRecord.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AuctionRecordListSerializer
        return AuctionRecordSerializer

    def get_queryset(self):
        queryset = AuctionRecord.objects.all()
        status_param = self.request.query_params.get('status')
        wine = self.request.query_params.get('wine')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if wine:
            queryset = queryset.filter(wine_id=wine)
        return queryset

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        auction = self.get_object()
        if auction.status != 'upcoming':
            return Response({'error': '只有即将开拍的拍卖才能开始'},
                            status=status.HTTP_400_BAD_REQUEST)
        auction.status = 'ongoing'
        auction.save()
        return Response(AuctionRecordSerializer(auction).data)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        auction = self.get_object()
        try:
            auction.end_auction()
            return Response(AuctionRecordSerializer(auction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def place_bid(self, request, pk=None):
        auction = self.get_object()
        customer_id = request.data.get('customer')
        amount = request.data.get('amount')

        if not customer_id or not amount:
            return Response({'error': '客户和出价金额必填'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': '客户不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            auction.place_bid(customer, Decimal(str(amount)))
            AuctionBid.objects.create(
                auction=auction,
                bidder=customer,
                amount=Decimal(str(amount))
            )
            return Response(AuctionRecordSerializer(auction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def bid_history(self, request, pk=None):
        auction = self.get_object()
        bids = auction.bids.all()
        return Response(AuctionBidSerializer(bids, many=True).data)


class SalesStatsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def overview(self, request):
        orders = SaleOrder.objects.filter(status__in=['confirmed', 'shipped', 'completed'])
        total_orders = orders.count()
        total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_customers = Customer.objects.count()
        total_auctions = AuctionRecord.objects.filter(status='ended').count()

        by_status = {}
        for status_code, status_label in SaleOrder.STATUS_CHOICES:
            by_status[status_code] = {
                'label': status_label,
                'count': SaleOrder.objects.filter(status=status_code).count()
            }

        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        monthly_sales = orders.filter(order_date__gte=six_months_ago) \
            .annotate(month=TruncMonth('order_date')) \
            .values('month') \
            .annotate(total=Sum('total_amount'), count=Count('id')) \
            .order_by('month')

        by_month = []
        for item in monthly_sales:
            by_month.append({
                'month': item['month'].strftime('%Y-%m'),
                'total': float(item['total']),
                'count': item['count']
            })

        top_customers = Customer.objects.order_by('-total_purchases')[:10]
        top_customers_data = []
        for customer in top_customers:
            top_customers_data.append({
                'id': customer.id,
                'name': customer.name,
                'total_purchases': float(customer.total_purchases),
                'total_orders': customer.total_orders,
                'level': customer.level,
                'level_display': customer.get_level_display()
            })

        return Response({
            'total_orders': total_orders,
            'total_sales': float(total_sales),
            'total_customers': total_customers,
            'total_auctions': total_auctions,
            'by_status': by_status,
            'by_month': by_month,
            'top_customers': top_customers_data,
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_register(request):
    phone = request.data.get('phone')
    password = request.data.get('password')
    name = request.data.get('name')
    gender = request.data.get('gender', '')
    email = request.data.get('email', '')
    id_card = request.data.get('id_card', '')
    address = request.data.get('address', '')

    if not phone or not password or not name:
        return Response({'error': '手机号、姓名、密码必填'}, status=status.HTTP_400_BAD_REQUEST)

    if Customer.objects.filter(phone=phone).exists():
        return Response({'error': '该手机号已注册'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=phone).exists():
        return Response({'error': '该手机号已注册'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=phone, password=password, email=email)
    customer = Customer.objects.create(
        user=user,
        name=name,
        phone=phone,
        gender=gender,
        email=email,
        id_card=id_card,
        address=address
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'role': 'customer',
            'level': customer.level,
            'level_display': customer.get_level_display()
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_info(request):
    user = request.user
    is_staff = user.is_staff or user.is_superuser

    data = {
        'username': user.username,
        'email': user.email,
        'role': 'admin' if is_staff else 'customer',
    }

    if not is_staff:
        try:
            customer = Customer.objects.get(user=user)
            data.update({
                'customer_id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'level': customer.level,
                'level_display': customer.get_level_display(),
                'total_purchases': float(customer.total_purchases),
                'total_orders': customer.total_orders
            })
        except Customer.DoesNotExist:
            pass

    return Response(data)
