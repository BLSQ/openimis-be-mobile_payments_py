import datetime
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import json
from retrying import retry
import threading
from django.core.cache import cache

logger = logging.getLogger(__name__)

lock = threading.Lock()

def access_token():
    # make it thread safe
    with lock:
        try:
            NOW = datetime.now()
            access_token = get_access_token()
            return {"Authorization": f"Bearer {access_token}"}
        except Exception as e:
            logging.exception("failed to get access token")
            return e


def get_access_token():
    api_token = cache.get('api_token')
    api_expiry_date = cache.get('api_expiry_date')

    if api_token is None:
        new_api_token, new_expiry_date = requests_new_access_token()
        cache.set('api_token', new_api_token)
        cache.set('api_expiry_date', new_expiry_date)
        return new_api_token
    elif api_expiry_date < datetime.now():
        cache.delete('api_token')
        cache.delete('api_expiry_date')

        new_api_token, new_expiry_date = requests_new_access_token()
        cache.set('api_token', new_api_token)
        cache.set('api_expiry_date', new_expiry_date)
        return new_api_token
    return api_token
    

@retry(stop_max_attempt_number=3, wait_fixed=60000, retry_on_exception=lambda exc: isinstance(exc, requests.exceptions.RequestException))
def requests_new_access_token():
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
            return new_token, new_expiry_date
        return None
    except requests.exceptions.RequestException as exc:
        logger.exception(f"Retrying due to: {str(exc)}")
        return ({
                    'message': _("fail to get a new token"),
                    'detail': str(exc)})