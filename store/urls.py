from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path(
        'products/<slug:slug>/comments/',
        views.CommentList.as_view(),
        name='comment-list'
    ),
    path(
        'products/<slug:slug>/',
        views.ProductDetail.as_view(),
        name='product-detail'
    ),
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('customers/me/', views.CustomerDetail.as_view(), name='customer-me'),
    path('carts/', views.CartList.as_view(), name='cart-list'),
    path('carts/<uuid:pk>/', views.CartDetail.as_view(), name='cart-detail'),
    path(
        'carts/<uuid:pk>/items/',
        views.CartItemList.as_view(),
        name='cart-item-list'
    ),
    path(
        'carts/<uuid:pk>/items/<int:cart_item_pk>/',
        views.CartItemDetail.as_view(),
        name='cart-item-detail'
    ),
    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
]
