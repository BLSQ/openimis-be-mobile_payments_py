import core
from django.test import TestCase
from insuree.models import Relation
from mobile_payment.models import PaymentServiceProvider, PaymentTransaction
from insuree.test_helpers import create_test_insuree
from core.test_helpers import create_test_interactive_user
from product.test_helpers import create_test_product
from policy.test_helpers import create_test_policy
from mobile_payment.tests.test_helpers import create_test_payment_service_provider_is_not_external_api_user, create_test_payment_service_provider_is_external_api_user, create_test_payment_transaction, update_payment_transaction
from django.utils import timezone

class TestMobilePaymentHelpers(TestCase):

    def test_create_test_payment_service_provider_is_not_external_api_user(self):
        paymentServiceProvider = create_test_payment_service_provider_is_not_external_api_user()
        self.assertIsInstance(paymentServiceProvider, PaymentServiceProvider)
        self.assertEqual(paymentServiceProvider.name, "Kashma")
        self.assertEqual(paymentServiceProvider.is_external_api_user, False)
        # Add more assertions as needed for the created object's attributes
    
    def test_create_test_payment_service_provider_is_external_api_user(self):
        username= create_test_interactive_user(username='test_user')
        paymentServiceProvider = create_test_payment_service_provider_is_external_api_user(username)
        self.assertIsInstance(paymentServiceProvider, PaymentServiceProvider)
        self.assertEqual(paymentServiceProvider.name, "Afrimoney")
        self.assertEqual(paymentServiceProvider.is_external_api_user, True)
        # Add more assertions as needed for the created object's attributes
    
    def test_create_test_payment_transaction(self):
        paymentTransaction = create_test_payment_transaction()
        self.assertIsInstance(paymentTransaction, PaymentTransaction)
        self.assertEqual(paymentTransaction.amount, 1000)
        self.assertEqual(paymentTransaction.otp, None)
        # Add more assertions as needed for the created object's attributes
    
    def test_update_payment_transaction(self):
        transaction = create_test_payment_transaction()
        update_props = {
            'amount': 1000.00,
            'psp_transaction_id': 'txn_84y4838y3y38',
            'otp': '654321',
            'status': True,
            'json_content': '{}'
        }
        update_payment_transaction(transaction, update_props)
        updated_transaction = PaymentTransaction.objects.get(pk=transaction.pk)
        self.assertEqual(updated_transaction.amount, 1000.00)
        self.assertEqual(updated_transaction.otp, "654321")
        self.assertEqual(updated_transaction.psp_transaction_id, 'txn_84y4838y3y38')
        # Add more assertions as needed for the updated object's attributes