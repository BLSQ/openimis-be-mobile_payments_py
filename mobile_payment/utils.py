import datetime
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import json
from .models import ApiUtilitie
import threading

logger = logging.getLogger(__name__)

lock = threading.Lock()

def access_token():
    # make it thread safe
    with lock:
        try:
            NOW = datetime.now()
            api_name = 'Qmoney_token'
            access_token = get_access_token(api_name)
            return {"Authorization": f"Bearer {access_token}"}
        except Exception as e:
            logging.exception("failed to get access token")
            return e


def get_access_token(api_name):
    api_utility = ApiUtilitie.objects.get(name=api_name)
    current_token = api_utility.access_token
    token_expiry_date = api_utility.access_TokenExpiry

    if token_expiry_date is None or token_expiry_date <= datetime.now():
        new_access_token, new_expiry_date = requests_new_access_token(api_name)

        api_utility.access_token = new_access_token
        api_utility.access_TokenExpiry = new_expiry_date
        api_utility.save()

        return new_access_token

    return current_token


def requests_new_access_token(api_name):
    try:
        auth_url =settings.PSP_QMONEY_AUTH_URL
        grantype=settings.PSP_QMONEY_GRANTTYPE
        username = settings.PSP_QMONEY_USERNAME
        password = settings.PSP_QMONEY_PASSWORD
        authBearerToken=settings.PSP_QMONEY_AUTH_BEARER_TOKEN
        data ={  
            "grantType": grantype, 
            "username":  username, 
            "password": password 
        }


        headers = {
                "Content-Type": "application/json", 
                "Authorization": f"Basic {authBearerToken}"
                }


        response = requests.post(auth_url, headers=headers, data=json.dumps(data), timeout=5)
        response_data = response.json()
        if response.status_code in [200,201] and response_data['responseCode'] == '1':
            new_token = response_data ['data']['access_token']
            expiry_seconds = int(response_data['data']['accessTokenExpiry']) - 60
            new_expiry_date = datetime.now() + timedelta(seconds=expiry_seconds)
            return new_token,new_expiry_date
        return None
    except requests.exceptions.RequestException as exc:
        return [{
                    'message': _("fail to get a new token"),
                    'detail': str(exc)}]