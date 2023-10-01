from django.dispatch import receiver

from store.signals import order_created


@receiver(order_created)
def send_email_to_customer(sender, **kwargs):
    print(f'SENDING EMAIL TO CUSTOMER FOR NEW ORDER: {kwargs["order"].pk}')
