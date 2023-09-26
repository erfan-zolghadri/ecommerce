from django_filters import rest_framework as filters

from . import models


class ProductFilter(filters.FilterSet):
    class Meta:
        model = models.Product
        fields = {
            'price': ['gt', 'lt'],
            'category_id': ['exact']
        }
