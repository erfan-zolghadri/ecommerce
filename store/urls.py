from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'store'

router = SimpleRouter()
router.register('categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),

    path('products/<int:pk>/comments/', views.CommentList.as_view(), name='comment-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('products/', views.ProductList.as_view(), name='product-list'),
]
