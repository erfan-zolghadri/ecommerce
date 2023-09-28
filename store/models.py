from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{str(self.discount)} | {self.description}'


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    discounts = models.ManyToManyField(Discount, blank=True)

    def __str__(self):
        return self.title


class CommentManager(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(status=Comment.STATUS_APPROVED)


class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Comment.STATUS_APPROVED)


class Comment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_NOT_APPROVED = 'not approved'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not approved')
    ]

    name = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    objects = CommentManager()
    approved = ApprovedCommentManager()


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()}'


class Address(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=500)
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        primary_key=True
    )

    class Meta:
        verbose_name_plural = 'addresses'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart id={self.id}'


class CartItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_item'
            )
        ]

    def __str__(self):
        return f'CartItem id={self.id}'


class UnpaidOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.STATUS_UNPAID)


class Order(models.Model):
    STATUS_PAID = 'paid'
    STATUS_UNPAID = 'unpaid'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_PAID, 'Paid'),
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_CANCELED, 'Canceled')
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_UNPAID
    )
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    objects = models.Manager()
    unpaid = UnpaidOrderManager()

    def __str__(self):
        return f'Order id={self.id}'


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_item'
            )
        ]
