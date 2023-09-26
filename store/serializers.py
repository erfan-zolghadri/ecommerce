from decimal import Decimal

from rest_framework import serializers

from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'title', 'description']


class ProductSerializer(serializers.ModelSerializer):
    TAX = 0.09

    price_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ['id', 'title', 'price', 'price_after_tax', 'stock', 'category']

    def get_price_after_tax(self, product):
        return round(
            product.price * Decimal(1 + ProductSerializer.TAX),
            ndigits=2
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['name', 'body', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.Comment.objects.create(
            product_id=product_id,
            **validated_data
        )
