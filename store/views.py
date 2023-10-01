from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from store import models
from store import serializers
from store.filters import ProductFilter
from store.paginations import DefaultPagination
from store.signals import order_created


class CategoryList(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().order_by('title')


class ProductList(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.select_related('category') \
        .order_by('-created_at')
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title']
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at']
    pagination_class = DefaultPagination


class ProductDetail(generics.RetrieveAPIView):
    serializer_class = serializers.ProductDetailSerializer
    queryset = models.Product.objects.select_related('category')
    lookup_field = 'slug'


class CommentList(generics.ListCreateAPIView):
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        product_slug = self.kwargs['slug']
        return models.Comment.objects.filter(product__slug=product_slug) \
            .order_by('-created_at')

    def get_serializer_context(self):
        product_slug = self.kwargs['slug']
        return {'product_slug': product_slug}


class CustomerDetail(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CustomerSerializer
    queryset = models.Customer.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return models.Customer.objects.select_related('user') \
            .get(user_id=self.request.user.id)


class CartList(generics.CreateAPIView):
    serializer_class = serializers.CartSerializer
    queryset = models.Cart.objects.all()


class CartDetail(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.CartSerializer
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'

    def get_queryset(self):
        return models.Cart.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=models.CartItem.objects.select_related('product')
            )
        )


class CartItemList(generics.ListCreateAPIView):
    def get_queryset(self):
        cart_id = self.kwargs['pk']
        return models.CartItem.objects.filter(cart_id=cart_id) \
            .select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CartItemCreateSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        cart_id = self.kwargs['pk']
        return {'cart_id': cart_id}


class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'patch', 'delete']

    def get_object(self):
        cart_item_pk = self.kwargs['cart_item_pk']
        return get_object_or_404(
            models.CartItem.objects.select_related('product'),
            pk=cart_item_pk
        )

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.CartItemUpdateSerializer
        return serializers.CartItemSerializer


class OrderList(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Order.objects.filter(customer__user_id=self.request.user.pk) \
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=models.OrderItem.objects.select_related('product')
                )
            )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.OrderCreateSerializer
        return serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.OrderCreateSerializer(
            data=request.data,
            context={'user_pk': self.request.user.pk}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        order_created.send_robust(sender=self.__class__, order=order)

        order_serializer = serializers.OrderSerializer(order)        
        return Response(order_serializer.data)


class OrderDetail(generics.RetrieveAPIView):
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Order.objects.filter(customer__user_id=self.request.user.pk) \
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=models.OrderItem.objects.select_related('product')
                )
            )
