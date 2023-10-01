from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from store import models

PRODUCT_PRICE_TAX = 0.09


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['pk', 'title']


class ProductSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField()
    category = CategorySerializer()

    class Meta:
        model = models.Product
        fields = [
            'pk', 'title', 'price',
            'price_after_tax', 'category'
        ]

    def get_price_after_tax(self, product):
        return round(
            product.price * Decimal(1 + PRODUCT_PRICE_TAX),
            ndigits=2
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField()
    category = CategorySerializer()

    class Meta:
        model = models.Product
        fields = [
            'pk', 'title', 'description', 'price',
            'price_after_tax', 'category'
        ]

    def get_price_after_tax(self, product):
        return round(
            product.price * Decimal(1 + PRODUCT_PRICE_TAX),
            ndigits=2
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['pk', 'name', 'body', 'created_at']

    def create(self, validated_data):
        product_slug = self.context['product_slug']
        product = models.Product.objects.get(slug=product_slug)
        return models.Comment.objects.create(
            product=product,
            **validated_data
        )


class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, source='user.first_name')
    last_name = serializers.CharField(max_length=150, source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = models.Customer
        fields = [
            'pk', 'first_name', 'last_name', 'email',
            'phone_number', 'birth_date'
        ]


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['pk', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.CartItem
        fields = ['pk', 'quantity', 'product', 'total']

    def get_total(self, cart_item):
        return cart_item.quantity * cart_item.product.price


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity', 'product']

    def create(self, validated_data):
        cart_id = self.context['cart_id']
        quantity = validated_data.get('quantity')
        product = validated_data.get('product')

        try:
            cart_item = models.CartItem.objects.get(cart_id=cart_id, product=product)
            cart_item.quantity += quantity
            cart_item.save()
        except models.CartItem.DoesNotExist:
            cart_item = models.CartItem.objects.create(
                cart_id=cart_id,
                **validated_data
            )

        self.instance = cart_item
        return cart_item


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.Cart
        fields = ['pk', 'items', 'total']

    def get_total(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['pk', 'title']


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderItem
        fields = ['pk', 'product', 'quantity', 'price', 'total']

    def get_total(self, order_item):
        return order_item.quantity * order_item.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.Order
        fields = ['pk', 'status', 'created_at', 'items', 'total']
        read_only_fields = ['status']

    def get_total(self, order):
        return sum([item.quantity * item.price for item in order.items.all()])


class OrderCreateSerializer(serializers.Serializer):
    cart_pk = serializers.UUIDField()

    def validate_cart_pk(self, cart_pk):
        if not models.Cart.objects.filter(pk=cart_pk).exists():
            raise serializers.ValidationError('Cart with this id does not exist.')

        if models.CartItem.objects.filter(cart_id=cart_pk).count() == 0:
            raise serializers.ValidationError('Cart is empty.')

        return cart_pk

    def save(self, **kwargs):
        with transaction.atomic():
            cart_pk = self.validated_data['cart_pk']
            user_pk = self.context['user_pk']
            customer = models.Customer.objects.get(user_id=user_pk)

            order = models.Order()
            order.customer_id = customer.pk
            order.save()

            cart_items = models.CartItem.objects.filter(cart_id=cart_pk) \
                .select_related('product')

            order_items = [
                models.OrderItem(
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    order_id=order.pk,
                    product_id=cart_item.product_id
                )
                for cart_item in cart_items
            ]

            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.get(pk=cart_pk).delete()
            return order
