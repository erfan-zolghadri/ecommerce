from django.contrib import admin
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


def pluralize_objects(objects_count):
    if objects_count == 1:
        return ' was'
    return 's were'


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'products_count']
    list_display_links = ['id', 'title']
    list_per_page = 10
    search_fields = ['title__istartswith']
    ordering = ['title']

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(products_count=Count('products'))

    @admin.display(description='#products', ordering='products_count')
    def products_count(self, category):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({'category_id': category.id})
        )
        return format_html(
            '<a href="{url}">{products_count}</a>',
            url=url,
            products_count=category.products_count
        )


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'discount']


class StockFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    GREATER_THAN_10 = '>10'

    title = 'Critical Stock Status'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return [
            (StockFilter.LESS_THAN_3, 'High'),
            (StockFilter.BETWEEN_3_AND_10, 'Medium'),
            (StockFilter.GREATER_THAN_10, 'OK')
        ]
    
    def queryset(self, request, queryset):
        if self.value() == StockFilter.LESS_THAN_3:
            return queryset.filter(stock__lt=3)

        if self.value() == StockFilter.BETWEEN_3_AND_10:
            return queryset.filter(stock__range=(3, 10))

        if self.value() == StockFilter.GREATER_THAN_10:
            return queryset.filter(stock__gt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'stock', 'category',
        'comments_count', 'price'
    ]
    list_display_links = ['id', 'title']
    list_editable = ['price']
    list_filter = ['created_at', StockFilter]
    list_per_page = 10
    autocomplete_fields = ['category']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['title__istartswith']

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(comments_count=Count('comments'))

    @admin.display(description='#comments', ordering='comments_count')
    def comments_count(self, product):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({'product_id': product.id})
        )
        return format_html(
            '<a href="{url}">{comments_count}</a>',
            url=url,
            comments_count=product.comments_count
        )


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status']
    list_editable = ['status']
    list_filter = ['status']
    list_per_page = 10
    autocomplete_fields = ['product']
    readonly_fields = ['created_at']
    search_fields = ['product__title__istartswith']
    actions = ['set_as_pending', 'set_as_approved', 'set_as_not_approved']

    @admin.action(description='Set as pending')
    def set_as_pending(self, request, queryset):
        updated_counts = queryset.update(status=models.Comment.STATUS_PENDING)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as pending.'
        )

    @admin.action(description='Set as approved')
    def set_as_approved(self, request, queryset):
        updated_counts = queryset.update(status=models.Comment.STATUS_APPROVED)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as approved.'
        )

    @admin.action(description='Set as not approved')
    def set_as_not_approved(self, request, queryset):
        updated_counts = queryset.update(status=models.Comment.STATUS_NOT_APPROVED)
        pluralized_comments = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} comment{pluralized_comments} set as not approved.'
        )


class AddressInline(admin.TabularInline):
    model = models.Address
    fields = ['customer', 'province', 'city']
    extra = 0


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    list_display_links = ['email']
    list_per_page = 10
    search_fields = [
        'user__first_name__istartswith',
        'user__last_name__istartswith'
    ]
    ordering = ['user__last_name', 'user__first_name']
    inlines = [AddressInline]

    def first_name(self, customer):
        return customer.user.first_name

    def last_name(self, customer):
        return customer.user.last_name

    def email(self, customer):
        return customer.user.email


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'province', 'city']
    list_display_links = ['customer']
    list_per_page = 10
    autocomplete_fields = ['customer']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class CartItemInline(admin.TabularInline):
    model = models.CartItem
    fields = ['product', 'quantity']
    extra = 0
    min_num = 1


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'total']
    list_filter = ['created_at']
    list_per_page = 10
    readonly_fields = ['created_at']
    inlines = [CartItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(total=ExpressionWrapper(
                Sum(F('items__quantity') * F('items__product__price')),
                output_field=DecimalField()
            ))

    @admin.display(ordering='total')
    def total(self, cart):
        return cart.total


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'price', 'total']
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(total=ExpressionWrapper(
                F('quantity') * F('product__price'),
                output_field=DecimalField()
            ))

    def total(self, cart_item):
        return cart_item.total
    
    def price(self, cart_item):
        return cart_item.product.price


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ['quantity', 'price', 'product']
    extra = 0
    min_num = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total', 'status']
    list_editable = ['status']
    list_filter = ['created_at', 'status']
    list_per_page = 10
    readonly_fields = ['created_at']
    actions = ['set_as_paid', 'set_as_unpaid', 'set_as_canceled']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(
                total=ExpressionWrapper(
                    Sum(F('items__quantity') * F('items__price')),
                    output_field=DecimalField()
                )
            )

    @admin.display(ordering='total')
    def total(self, order):
        return order.total
    
    @admin.action(description='Set as paid')
    def set_as_paid(self, request, queryset):
        updated_counts = queryset.update(status=models.Order.STATUS_PAID)
        pluralized_orders = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} order{pluralized_orders} set as paid.'
        )

    @admin.action(description='Set as unpaid')
    def set_as_unpaid(self, request, queryset):
        updated_counts = queryset.update(status=models.Order.STATUS_UNPAID)
        pluralized_orders = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} order{pluralized_orders} set as unpaid.'
        )

    @admin.action(description='Set as canceled')
    def set_as_canceled(self, request, queryset):
        updated_counts = queryset.update(status=models.Order.STATUS_CANCELED)
        pluralized_orders = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f'{updated_counts} order{pluralized_orders} set as canceled.'
        )


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'total']
    list_per_page = 10
    autocomplete_fields = ['product']

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(total=ExpressionWrapper(
                Sum(F('quantity') * F('price')),
                output_field=DecimalField()
            ))

    @admin.display(ordering='total')
    def total(self, order):
        return order.total
