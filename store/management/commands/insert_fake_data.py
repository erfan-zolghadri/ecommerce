from datetime import datetime, timedelta
import random

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from store import factories
from store import models

CATEGORIES_COUNT = 100
DISCOUNTS_COUNT = 10
PRODUCTS_COUNT = 500
CUSTOMERS_COUNT = 100
CARTS_COUNT = 100
ORDERS_COUNT = 50

store_models = [
    models.CartItem,
    models.Cart,
    models.OrderItem,
    models.Order,
    models.Product,
    models.Category,
    models.Comment,
    models.Discount,
    models.Address,
    models.Customer
]

faker = Faker()


class Command(BaseCommand):
    help = 'Inserts fake data to database'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        for model in store_models:
            model.objects.all().delete()
        self.stdout.write('Old data deleted')

        # Generate categories
        print(f'Inserting {CATEGORIES_COUNT} categories...', end='')
        categories = [factories.CategoryFactory() for _ in range(CATEGORIES_COUNT)]
        print('Done')

        # Generate discounts
        print(f'Inserting {DISCOUNTS_COUNT} discounts...', end='')
        for _ in range(DISCOUNTS_COUNT):
            factories.DiscountFactory()
        print('Done')

        # Generate products
        print(f'Inserting {PRODUCTS_COUNT} product...', end='')
        products = list()
        for _ in range(PRODUCTS_COUNT):
            product = factories.ProductFactory(category_id=random.choice(categories).id)
            product.created_at = datetime(
                random.randrange(2019, 2023),
                random.randint(1,12),
                random.randint(1,12),
                tzinfo=timezone.utc
            )
            product.updated_at = product.created_at + timedelta(hours=random.randint(1, 500))
            product.save()
            products.append(product)
        print('Done')

        # Generate comments
        print(f'Inserting product comments...', end='')
        for product in products:
            for _ in range(random.randint(1, 5)):
                comment = factories.CommentFactory(product_id=product.id)
                comment.created_at = datetime(
                    random.randrange(2019, 2023),
                    random.randint(1,12),
                    random.randint(1,12),
                    tzinfo=timezone.utc
                )
                comment.save()
        print('Done')

        # Generate customers
        print(f'Inserting {CUSTOMERS_COUNT} customers...', end='')
        customers = [
            (factories.CustomerFactory() \
            if (random.random() > 0.3) \
            else factories.CustomerFactory(birth_date=None)) \
            for _ in range(CUSTOMERS_COUNT)
        ]
        print('Done')

        # Generate addresses
        print(f'Inserting customers addresses...', end='')
        for customer in customers:
            factories.AddressFactory(customer_id=customer.id)
        print('Done')

        # Generate carts
        print(f'Inserting {CARTS_COUNT} carts...', end='')
        carts = list()
        for _ in range(CARTS_COUNT):
            cart = factories.CartFactory()
            cart.created_at = datetime(
                random.randrange(2022, 2023),
                random.randint(1,12),
                random.randint(1,12),
                tzinfo=timezone.utc
            )
            cart.save()
            carts.append(cart)
        print('Done')

        # Generate cart items
        print(f'Inserting cart items...', end='')
        cart_items = list()
        for cart in carts:
            random_products = random.sample(products, k=random.randint(1, 10))
            for product in random_products:
                cart_item = factories.CartItemFactory(
                    cart_id=cart.id,
                    product_id=product.id,
                )
                cart_items.append(cart_item)
        print('Done')

        # Generate orders
        print(f'Inserting {ORDERS_COUNT} orders...', end='')
        orders = [
            factories.OrderFactory(customer_id=random.choice(customers).id) \
            for _ in range(ORDERS_COUNT)
        ]
        for order in orders:
            order.created_at = datetime(
                random.randrange(2019, 2023),
                random.randint(1,12),
                random.randint(1,12),
                tzinfo=timezone.utc
            )
            order.save()
        print('Done')

        # Generate order items
        print(f'Inserting order items...', end='')
        order_items = list()
        for order in orders:
            random_products = random.sample(products, random.randint(1, 10))
            for product in random_products:
                order_item = factories.OrderItemFactory(
                    order_id=order.id,
                    product_id=product.id,
                    price=product.price
                )
                order_items.append(order_item)
        print('Done')
