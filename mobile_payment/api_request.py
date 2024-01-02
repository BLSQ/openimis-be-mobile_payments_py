import requests
import json
import logging
import os
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .utils import access_token  
from retrying import retry
from .exception import InitiatePaymentRequestFailedException, ProcessPaymentRequestFailedException,ProcessPaymentRequestFailedException                                                                                                                                                   
logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=3, wait_fixed=30000, retry_on_exception=lambda exc: isinstance(exc, requests.exceptions.RequestException))
def initiate_request(insuree_wallet:str, merchant_wallet:str, amount:float, pin:str) :
    try:
        url = settings.PSP_QMONEY_URL_PAYMENT
        tokens = access_token()

        payload = json.dumps({
            "data": {
                "fromUser": {
                "userIdentifier": insuree_wallet
                },
                "toUser": {
                "userIdentifier": merchant_wallet
                },
                "serviceId": "MOBILE_MONEY",
                "productId": "NHIA_GETMONEY",
                "remarks": "add", 
                "payment": [
                {
                    "amount": amount
                }
                ],
                "transactionPin": pin
            }
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": tokens['Authorization']
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_data = response.json()
        if response.status_code in [200,201] and response_data['responseCode'] == '1':
            return response_data 
        else:
            raise InitiatePaymentRequestFailedException(response_data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    except requests.exceptions.RequestException as exc:
         logger.exception(f"Retrying due to: {str(exc)}")
         raise InitiatePaymentRequestFailedException ({
                    'message': _("Payment request failed"),
                    'detail': str(exc)})
    
@retry(stop_max_attempt_number=3, wait_fixed=30000, retry_on_exception=lambda exc: isinstance(exc, requests.exceptions.RequestException))
def process_request(otp: str, transaction_id: str,) :
    try:
        url = settings.PSP_QMONEY_URL_PROCESS
        tokens = access_token()

        payload = json.dumps({
            "data": {
                "otp": otp,
                "transactionId": transaction_id
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Authorization': tokens['Authorization'] 
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_data = response.json()
        if response.status_code in [200,201]:
            return response_data
        else:
            raise ProcessPaymentRequestFailedException(response_data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    except requests.exceptions.RequestException as exc:
        logger.exception(f"Retrying due to: {str(exc)}")
        raise ProcessPaymentRequestFailedException ({
                    'message': _("Payment Process failed "),
                    'detail': str(exc)})
    









