from rest_framework import serializers
from .models import Customer, SaleOrder, SaleOrderItem, AuctionRecord, AuctionBid


class CustomerSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class CustomerListSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'level', 'level_display',
                  'total_purchases', 'total_orders', 'created_at']


class SaleOrderItemSerializer(serializers.ModelSerializer):
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)
    wine_image = serializers.CharField(source='wine.image_url', read_only=True)

    class Meta:
        model = SaleOrderItem
        fields = '__all__'


class SaleOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderItem
        fields = ['id', 'wine', 'quantity', 'unit_price', 'notes']


class SaleOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    items = SaleOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = SaleOrder
        fields = '__all__'


class SaleOrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = SaleOrder
        fields = ['id', 'order_no', 'customer', 'customer_name', 'status', 'status_display',
                  'total_amount', 'order_date', 'created_at']


class SaleOrderCreateSerializer(serializers.ModelSerializer):
    items = SaleOrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = SaleOrder
        fields = ['customer', 'discount', 'shipping_fee', 'payment_method',
                  'shipping_address', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = SaleOrder.objects.create(**validated_data)
        subtotal = 0
        for item_data in items_data:
            item = SaleOrderItem.objects.create(order=order, **item_data)
            subtotal += item.total_price
        order.subtotal = subtotal
        order.save()
        return order


class AuctionBidSerializer(serializers.ModelSerializer):
    bidder_name = serializers.CharField(source='bidder.name', read_only=True)

    class Meta:
        model = AuctionBid
        fields = '__all__'


class AuctionRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)
    wine_image = serializers.CharField(source='wine.image_url', read_only=True)
    winner_name = serializers.CharField(source='winner.name', read_only=True, default=None)
    bids = AuctionBidSerializer(many=True, read_only=True)

    class Meta:
        model = AuctionRecord
        fields = '__all__'


class AuctionRecordListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    wine_name = serializers.CharField(source='wine.name', read_only=True)
    wine_vintage = serializers.IntegerField(source='wine.vintage', read_only=True)

    class Meta:
        model = AuctionRecord
        fields = ['id', 'title', 'wine', 'wine_name', 'wine_vintage', 'quantity',
                  'start_price', 'current_bid', 'final_price', 'status', 'status_display',
                  'start_time', 'end_time', 'bid_count']


class SalesStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_customers = serializers.IntegerField()
    total_auctions = serializers.IntegerField()
    by_status = serializers.DictField()
    by_month = serializers.ListField()
    top_customers = serializers.ListField()
