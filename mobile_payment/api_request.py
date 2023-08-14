import requests
import json
import os
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .utils import access_token                                                                                                                                                    



def initiate_request(insuree_wallet:str, merchant_wallet:str, amount:float, pin:str) :
    try:
        url = settings.QCELL_URL_PAYMENT
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
        return None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    except requests.exceptions.RequestException as exc:
         return [{
                    'message': _("Payment request failed with exception"),
                    'detail': str(exc)}]





def process_request(otp: str, transaction_id: str,) :
    try:
        url = settings.QCELL_URL_PROCESS
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
        if response.status_code in [200,201] and response_data['responseCode'] == '1':
            return response_data
        return None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    except requests.exceptions.RequestException as exc:
        print(exc)
        return [{
                    'message': _("Payment request failed with exception"),
                    'detail': str(exc)}]

    









