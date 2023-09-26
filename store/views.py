from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from . import models
from . import serializers
from .filters import ProductFilter
from .paginations import DefaultPagination


class CategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()


class ProductList(ListAPIView):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title']
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at']
    pagination_class = DefaultPagination


class ProductDetail(RetrieveAPIView):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()


class CommentList(ListCreateAPIView):
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        product_id = self.kwargs['pk']
        return models.Comment.objects.filter(product_id=product_id)

    def get_serializer_context(self):
        product_id = self.kwargs['pk']
        return {'product_id': product_id}
