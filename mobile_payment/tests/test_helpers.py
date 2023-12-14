from mobile_payment.models import PaymentServiceProvider, PaymentTransaction
from insuree.test_helpers import create_test_insuree
from django.utils import timezone
from django.conf import settings

def create_test_payment_service_provider_is_not_external_api_user(custom_props={}):
    from core import datetime
    return PaymentServiceProvider.objects.create(
        **{
            "name": "Kashma",
            "account": "123456789",
            "pin": "123456",
            "is_external_api_user": False,
            **custom_props
            
        }
    )

def create_test_payment_service_provider_is_external_api_user(username, custom_props={},):
    from core import datetime
    return PaymentServiceProvider.objects.create(
        **{
            "name": "Afrimoney",
            "account": "123456789",
            "interactive_user": username.i_user,
            "is_external_api_user": True,
            **custom_props    
        }
    )


def create_test_payment_transaction(custom_props={}):
    from core import datetime
    payment_service_provider = create_test_payment_service_provider_is_not_external_api_user()
    insuree = create_test_insuree()
    return PaymentTransaction.objects.create(
        **{
            "amount":1000.00,
            "payment_service_provider":payment_service_provider,
            "insuree": insuree,
            "psp_transaction_id": "txn_84y4838y3y38",
            "otp":None,
            "status":False,
            **custom_props    
        }
    )

def update_payment_transaction(payment_transaction, update_props):
    """
    Update a PaymentTransaction object with the provided properties.

    Args:
    - payment_transaction: The PaymentTransaction object to update.
    - update_props: A dictionary containing properties to update.

    Returns:
    - None
    """
    for key, value in update_props.items():
        setattr(payment_transaction, key, value)
    payment_transaction.save()

        