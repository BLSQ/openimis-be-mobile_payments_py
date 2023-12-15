import base64
import json
from dataclasses import dataclass
from core.models import User
import core
from core.test_helpers import create_test_interactive_user
from django.conf import settings
from graphene_django.utils.testing import GraphQLTestCase
from django.test import TestCase
from graphql_jwt.shortcuts import get_token
from mobile_payment.tests.test_helpers import create_test_payment_service_provider_is_external_api_user
from insuree.models import Relation
from rest_framework import status





### Mobile_Payment TestCases
    
@dataclass
class DummyContext:
    """ Just because we need a context to generate. """
    user: User
class MobilePaymentTestCases(GraphQLTestCase):
    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    GRAPHQL_SCHEMA = True
    admin_user = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_not_authorized = create_test_interactive_user(username="testuser2")
        cls.user_not_authorized_token = get_token(cls.user_not_authorized, DummyContext(user=cls.user_not_authorized))
        cls.user_authorized = create_test_interactive_user(username="testuser1")
        cls.psp = create_test_payment_service_provider_is_external_api_user(cls.user_authorized)
        cls.user_authorized_token = get_token(cls.user_authorized, DummyContext(user=cls.user_authorized))

    def test_verify_insuree_not_authorized_user(self):
        chf_id = "070707070" #pass in a valid isnuree_number here
        """
        assert that user trying to verify insuree is not authorized.

        Args:
            chf_id (str): The CHF ID of the insuree.

        Returns:
            None
        """
        response =  self.query(
            f'''
        {{
            verifyInsuree(chfId:"{chf_id}") {{
                lastName
                firstName
                message
                policies {{
                    amount
                    status
                    productName
                    productCode
                    token
                }}
            }}
        }}
        ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_not_authorized_token}"},

        )
        
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        # Check if response has errors
        self.assertIn('errors', content)
        #Extract the first error message
        error_messages = content['errors']
        error_message_list = error_messages[0]['message']
        error_message = ''.join(error_message_list)
        # Define the expected error message for unauthorized access
        expected_error_message = "['You are not authorized to perform this operation']"

        #Assert that the error message matches the expected message
        self.assertEqual(error_message_list, expected_error_message, f"Unexpected error message: {error_message_list}")

    def test_verify_insuree_does_not_have_idle_policy(self,):
        chf_id = "111111117" #pass in a valid isnuree_number here
        """
        Verify if the insuree is an authorizedand also assert insuree does not have any idle policy that requires payment.

        Args:
            cdf_id (str): The ID of the insuree.

        Returns:
            None
        """
        response = self.query(
        f'''
        {{
            verifyInsuree(chfId:"{chf_id}") {{
                lastName
                firstName
                message
                policies {{
                    amount
                    status
                    productName
                    productCode
                    token
                }}
            }}
        }}
        ''',
        headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},
    )
             

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertIn('verifyInsuree', content['data'])
        # Get the 'verifyInsuree' object
        verify_insuree_data = content['data']['verifyInsuree']
        # Check if the 'message' field contains the expected message
        expected_message = 'insuree does not have any idle policy that requires payment,'
        self.assertEqual(verify_insuree_data['message'], expected_message)

    def test_verify_insuree_chf_id_does_exist(self):
        chf_id = "0707070" #pass in an invalid isnuree_number here
        """
        assert that chf_id enetered is not valid.

        Args:
            chf_id (str): The CHF ID of the insuree.

        Returns:
            None
        """
        response =  self.query(
            f'''
        {{
            verifyInsuree(chfId:"{chf_id}") {{
                lastName
                firstName
                message
                policies {{
                    amount
                    status
                    productName
                    productCode
                    token
                }}
            }}
        }}
        ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},

        )
        
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        # Check if response has errors
        self.assertResponseNoErrors(response)
        self.assertIn('verifyInsuree', content['data'])
        # Get the 'verifyInsuree' object
        verify_insuree_data = content['data']['verifyInsuree']
        # Check if the 'message' field contains the expected message
        expected_message = 'chf_id does not exist'
        self.assertEqual(verify_insuree_data['message'], expected_message)
    
    def test_verify_insuree_display_idle_policies(self):
        chf_id = "070707070" #pass in an valid isnuree_number here with and idle policy
        """
        asserts that chf_id entered is valid and display the idle policies only.

        Args:
            chf_id (str): The CHF ID of the insuree that has idle policys

        Returns:
            None
        """
        response =  self.query(
            f'''
        {{
            verifyInsuree(chfId:"{chf_id}") {{
                lastName
                firstName
                message
                policies {{
                    amount
                    status
                    productName
                    productCode
                    token
                }}
            }}
        }}
        ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},

        )
        
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        print(f'chf_id2: {content}')
        # Check if response has errors
        self.assertResponseNoErrors(response)
        self.assertIn('verifyInsuree', content['data'])
        verify_insuree_data = content['data']['verifyInsuree']
        # Check the presence of specific keys
        expected_keys = ['lastName', 'firstName', 'message']
        for key in expected_keys:
            self.assertIn(key, verify_insuree_data)

        # Check the presence of specific keys inside 'policies'
        policies = verify_insuree_data.get('policies', [])
        for policy in policies:
            self.assertIn('status', policy)
            self.assertEqual(policy['status'], 1)
        return content
    
    def test_process_payment_mutation_amount_too_small(self):
        amount = "1000"
        chf_id = "070707070" #change the chf_id to an insuree that has an idle policy
        psp_transactionId = "txid_3845938338"
          # Call the first test case function to retrieve its returned content
        returned_content = self.test_verify_insuree_display_idle_policies()
        
        # Check if the 'verifyInsuree' key exists in the returned content
        self.assertIn('verifyInsuree', returned_content['data'])

        # Check if 'policies' key exists inside 'verifyInsuree' and it's a non-empty list
        self.assertIn('policies', returned_content['data']['verifyInsuree'])
        policies = returned_content['data']['verifyInsuree']['policies']
        self.assertTrue(isinstance(policies, list) and len(policies) > 0)
        # Extract data only if 'policies' list exists and has at least one element
        if policies:
            productName = policies[0].get('productName')
            productCode = policies[0].get('productCode')
            token = policies[0].get('token')


        response = self.query(
            f'''
            mutation {{
                processPayment(input: {{
                    chfId: "{chf_id}",
                    amount: "{amount}",
                    pspTransactionId: "{psp_transactionId}",
                    policy: {{
                        productName: "{productName}",
                        productCode: "{productCode}",
                        token: "{token}"
                    }}
                    
                }}) 
                {{
                    Success
                    responseMessage
                    detail     
                }}
            }}
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},
        )

        # Add assertions for the mutation response using response data
        # self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        process_payment_content = content['data']['processPayment']
        
 
        # Assert the 'message' value against the expected value
        expected_message = 'Amount is too small. It needs to be the exact amount of the product.'
        self.assertEqual (process_payment_content['responseMessage'],expected_message)
    
    def test_process_payment_mutation_amount_too_big(self):

        amount = "20000" #enter amount greater than the product price
        chf_id = "070707070" #eneter valid chf_id
        psp_transactionId = "txid_3845938338"
          # Call the first test case function to retrieve its returned content
        returned_content = self.test_verify_insuree_display_idle_policies()
        
        # Check if the 'verifyInsuree' key exists in the returned content
        self.assertIn('verifyInsuree', returned_content['data'])

        # Check if 'policies' key exists inside 'verifyInsuree' and it's a non-empty list
        self.assertIn('policies', returned_content['data']['verifyInsuree'])
        policies = returned_content['data']['verifyInsuree']['policies']
        self.assertTrue(isinstance(policies, list) and len(policies) > 0)
        # Extract data only if 'policies' list exists and has at least one element
        if policies:
            productName = policies[0].get('productName')
            productCode = policies[0].get('productCode')
            token = policies[0].get('token')


        response = self.query(
            f'''
            mutation {{
                processPayment(input: {{
                    chfId: "{chf_id}",
                    amount: "{amount}",
                    pspTransactionId: "{psp_transactionId}",
                    policy: {{
                        productName: "{productName}",
                        productCode: "{productCode}",
                        token: "{token}"
                    }} 
                }}) 
                {{
                    Success
                    responseMessage
                    detail
                }}
            }}
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},
        )

        # Add assertions for the mutation response using response data
        # self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        process_payment_content = content['data']['processPayment']

        # Assert the 'message' value against the expected value
        expected_message = 'Amount is too large. pls enter the exact amount the product cost.'
        self.assertEqual (process_payment_content['responseMessage'],expected_message)

    def test_process_payment_mutation_unauthorized_user(self):
        amount = "20000" #enter amount less than the product price
        chf_id = "070707070" #eneter valid chf_id
        psp_transactionId = "txid_3845938338"
          # Call the first test case function to retrieve its returned content
        returned_content = self.test_verify_insuree_display_idle_policies()
        
        # Check if the 'verifyInsuree' key exists in the returned content
        self.assertIn('verifyInsuree', returned_content['data'])

        # Check if 'policies' key exists inside 'verifyInsuree' and it's a non-empty list
        self.assertIn('policies', returned_content['data']['verifyInsuree'])
        policies = returned_content['data']['verifyInsuree']['policies']
        self.assertTrue(isinstance(policies, list) and len(policies) > 0)
        # Extract data only if 'policies' list exists and has at least one element
        if policies:
            productName = policies[0].get('productName')
            productCode = policies[0].get('productCode')
            token = policies[0].get('token')


        response = self.query(
            f'''
            mutation {{
                processPayment(input: {{
                    chfId: "{chf_id}",
                    amount: "{amount}",
                    pspTransactionId: "{psp_transactionId}",
                    policy: {{
                        productName: "{productName}",
                        productCode: "{productCode}",
                        token: "{token}"
                    }} 
                }}) 
                {{
                    Success
                    responseMessage
                    detail
                }}
            }}
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_not_authorized_token}"},
        )

        # Add assertions for the mutation response using response data
        # self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        process_payment_content = content['data']['processPayment']
        # Assert the 'message' value against the expected value
        expected_message = "['You are not authorized to perform this operation']"
        self.assertEqual (process_payment_content['detail'], expected_message) 
    

    def test_process_payment_mutation_success(self):
        amount = "10000" #enter amount == to the product price
        chf_id = "070707070" #eneter valid chf_id that has an idle policy
        psp_transactionId = "txid_3845938338"
        
          # Call the first test case function to retrieve its returned content
        returned_content = self.test_verify_insuree_display_idle_policies()
        
        # Check if the 'verifyInsuree' key exists in the returned content
        self.assertIn('verifyInsuree', returned_content['data'])

        # Check if 'policies' key exists inside 'verifyInsuree' and it's a non-empty list
        self.assertIn('policies', returned_content['data']['verifyInsuree'])
        policies = returned_content['data']['verifyInsuree']['policies']
        self.assertTrue(isinstance(policies, list) and len(policies) > 0)
        

        # Extract data only if 'policies' list exists and has at least one element
        if policies:
            productName = policies[0].get('productName')
            productCode = policies[0].get('productCode')
            token = policies[0].get('token')


        response = self.query(
            f'''
            mutation {{
                processPayment(input: {{
                    chfId: "{chf_id}",
                    amount: "{amount}",
                    pspTransactionId: "{psp_transactionId}",
                    policy: {{
                        productName: "{productName}",
                        productCode: "{productCode}",
                        token: "{token}"
                    }} 
                }}) 
                {{
                    Success
                    responseMessage
                    detail
                }}
            }}
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_authorized_token}"},
        )
        # Add assertions for the mutation response using response data
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        process_payment_content = content['data']['processPayment']
        print(process_payment_content)
        # Assert the 'message' value against the expected value
        self.assertEqual (process_payment_content['Success'], True)
        self.assertEqual (process_payment_content['responseMessage'], "Payment processed successfully")


   