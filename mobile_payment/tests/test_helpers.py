from mobile_payment.models import PaymentServiceProvider, PaymentTransaction
from insuree.test_helpers import create_test_insuree
from product.test_helpers import create_test_product
from  policy.test_helpers import create_test_policy
from policy.models import  Policy
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

def create_test_insuree_data_with_policy():
        insuree = create_test_insuree(with_family=True, 
                                      custom_props={
                                        "last_name": "Wolve",
                                        "other_names": "Lone",
                                        "chf_id": "80809090",
                                    },
                                   family_custom_props ={
                                        "validity_from": "2019-01-01",
                                        "head_insuree_id": 8,  # dummy
                                        "audit_user_id": -1,
                                     })
        product = create_test_product("WCR101",custom_props={
                                        "lump_sum": 10000.00,
                                        "max_members": 1,
                                        "grace_period_enrolment": 1,
                                        "insurance_period": 12,
                                        "date_from": "2024-01-01",
                                        "date_to": "2049-01-01",
                                     })
        policy = create_test_policy(product, insuree, custom_props={
            
                                     "status": Policy.STATUS_IDLE,
                                     "stage": Policy.STAGE_NEW,
                                     "enroll_date": "2023-12-31",
                                     "start_date": "2024-01-02",
                                     "validity_from": "2019-01-01",
                                     "effective_date": "2019-01-01",
                                  })
        return insuree, product, policy
    
