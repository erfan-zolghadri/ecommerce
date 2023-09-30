from decimal import Decimal

from djoser.serializers import UserSerializer
from rest_framework import serializers

from store import models

PRODUCT_PRICE_TAX = 0.09


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'title']


class ProductSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField()
    category = CategorySerializer()

    class Meta:
        model = models.Product
        fields = [
            'id', 'title', 'price',
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
            'id', 'title', 'description', 'price',
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
        fields = ['name', 'body', 'created_at']

    def create(self, validated_data):
        product_slug = self.context['product_slug']
        product = models.Product.objects.get(slug=product_slug)
        return models.Comment.objects.create(
            product=product,
            **validated_data
        )


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Customer
        fields = ['user', 'phone_number', 'birth_date']


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    total = serializers.SerializerMethodField()

    class Meta:
        model = models.CartItem
        fields = ['id', 'quantity', 'product', 'total']

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
        fields = ['id', 'items', 'total']

    def get_total(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])
