from datetime import datetime
import random

from factory.django import DjangoModelFactory
from faker import Faker
import factory

from . import models

faker = Faker()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.Category

    title = factory.LazyFunction(lambda: ' '.join([word.capitalize() for word in faker.words(2)]))
    description = factory.Faker('sentence')


class DiscountFactory(DjangoModelFactory):
    class Meta:
        model = models.Discount

    discount = factory.LazyFunction(lambda: random.randint(1, 80)/100)
    description = factory.Faker('sentence')


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = models.Product

    title = factory.LazyFunction(lambda: ' '.join([word.capitalize() for word in faker.words(3)]))
    slug = factory.LazyAttribute(lambda obj: '-'.join(obj.title.split(' ')).lower())
    description = factory.Faker('paragraph', nb_sentences=5, variable_nb_sentences=True)
    price = factory.LazyFunction(lambda: random.randint(1, 1000) + random.randint(0, 100)/100)
    stock = factory.LazyFunction(lambda: random.randint(1, 100))


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = models.Comment

    name = factory.Faker('name')
    body = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    status = factory.LazyFunction(lambda: random.choice([
        models.Comment.STATUS_PENDING,
        models.Comment.STATUS_APPROVED,
        models.Comment.STATUS_NOT_APPROVED
    ]))


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = models.Customer

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone_number = factory.Faker('msisdn')
    birth_date = factory.LazyFunction(lambda: faker.date_time_ad(
        start_datetime=datetime(1990, 1, 1),
        end_datetime=datetime(2010, 1, 1))
    )


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = models.Address

    province = factory.LazyFunction(lambda: faker.word().capitalize())
    city = factory.Faker('city')
    address = factory.Faker('address')


class CartFactory(DjangoModelFactory):
    class Meta:
        model = models.Cart


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = models.CartItem

    quantity = factory.LazyFunction(lambda: random.randint(1, 20))


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = models.Order

    status = factory.LazyFunction(lambda: random.choice([
        models.Order.STATUS_PAID,
        models.Order.STATUS_UNPAID,
        models.Order.STATUS_CANCELED
    ]))


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = models.OrderItem

    quantity = factory.LazyFunction(lambda: random.randint(1, 20))
