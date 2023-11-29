## openIMIS Backend Mobile_Payment Modoule
This repository holds the files of the openIMIS Backend payment reference module.


The Mobile Payment module is designed to enable seamless payment processing for insured policies. This module comprises two distinct workflows:

1. **Integration with Qmoney**: In this workflow, the module establishes a connection with the Qmoney payment service provider, facilitating secure and efficient payment processing for policyholders.

2. **Endpoint Exposition**: The module also exposes two essential endpoints, `verify_insuree` and `process_payment`. These endpoints can be utilized by other payment service providers seeking to offer policyholders the ability to make payments through their services. This flexibility allows for integration with a variety of payment providers, making it a versatile solution for policyholder payments..

Qmoney implementation requires two frontend module installed : [openimis-fe-contribution_js](https://github.com/BLSQ/openimis-fe-contribution_js/tree/develop).
and [openimis-fe-insuree_js](https://github.com/BLSQ/openimis-fe-insuree_js/tree/impl/gambia)
### ERP Diagram of Mobile Payment
![Entity Relationship Diagram](workflow/Mobile_Payment%20Database.jpg)

"Link to the workflow diagram and database of the Mobile Payment module can be found here [workflow](https://github.com/BLSQ/openimis-be-mobile_payments_py/tree/feature/gambia/workflow)


# Qmoney Integration Guide

Qmoney provides two essential mutations: `InitiateTransactionMutation` and `ProcessTransactionMutation`. These mutations enable seamless payment processing between accountants and insured individuals.

### Initiating a Transaction

To initiate a transaction, an accountant is required to select the following fields:
- `amount`
- `paymentServiceProviderUuid`
- `insureeUuid`

Upon selection, an OTP is generated by the Payment Service Provider and sent to the insuree's phone number. The insuree is responsible for sharing this OTP with the accountant. The accountant will then enter the OTP to proceed with the transaction.

### Processing a Transaction

When processing a transaction, the following fields are required:
- `uuid`
- `otp`
- `amount`
- `insureeUuid`
- `paymentServiceProvider`
- 

Once a transaction is initiated and successfully processed, it is added to the contribution table named "premium." The transaction details are stored by adding the transaction UUID to the "transaction_uuid" field, which acts as a foreign key.
### Note: 

### Qmoney Sequence Diagram

![Qmoney Sequence Diagram](workflow/Qmoney_Sequence%20Diagram.jpg)

### Note

For an insuree to receive an OTP, their Qmoney wallet information must be saved in the "insuree_wallet" field of the Insuree model. The status of a transaction is initially set to `0` when initiated and changes to `1` upon successful processing.


# Qmoney Testing Setup

Before you can begin testing with Qmoney, you need to configure the following variables in your `openimis-be_py/.env` file:

```env
************ Qmoney login credential*********************
PSP_QMONEY_GRANTTYPE=password
PSP_QMONEY_USERNAME=<YOUR_QMONEY_USERNAME>
PSP_QMONEY_PASSWORD=<YOUR_QMONEY_PASSWORD>
PSP_QMONEY_AUTH_BEARER_TOKEN=<YOUR_QMONEY_BEARER_TOKEN>

************ Qmoney urls *********************
PSP_QMONEY_AUTH_URL=<YOUR_QMONEY_AUTH_URL>
PSP_QMONEY_URL_INITIATE=<YOUR_QMONEY_URL_INITIATE>
PSP_QMONEY_URL_PROCESS=<YOUR_QMONEY_URL_PROCESS>

************ Qmoney Payment Service Provider account credential *********************

PSP_QMONEY_NAME=Qmoney 
PSP_QMONEY_ACCOUNT=<YOUR_QMONEY_ACCOUNT> 
PSP_QMONEY_PIN=<YOUR_QMONEY_PIN>

******************* Qmoney Api info **************************
QMONEY_API_NAME=Qmoney_token 
QMONEY_API_ACCESS_TOKEN=<YOUR_QMONEY_ACCESS_TOKEN>
QMONEY_API_ACCESS_TOKEN_EXPIRY=<YOUR_QMONEY_ACCESS_TOKEN_EXPIRY>

```
Ensure that you replace the placeholders <Grant Type>, <Authentication Username for Authorization>, and other placeholders with the actual values specific to your Qmoney configuration.
Note that only the field `QMONEY_API_NAME` with the value `Qmoney_token` remain the same, if not you will run into an error
These settings are crucial for creating a successful testing environment when working with Qmoney integration.

### Test use case sample
```
************ Qmoney login credential*********************
PSP_QMONEY_GRANTTYPE=password
PSP_QMONEY_USERNAME=14001502
PSP_QMONEY_PASSWORD=Nhia@123
PSP_QMONEY_AUTH_BEARER_TOKEN=TkhJQV9BQ0NFU1NfQ0hBTk5FTDpuaGlhQEAxMjM
*********** Qmoney urls *********************
PSP_QMONEY_AUTH_URL=https://uat-adpelite.qmoney.gm/login
PSP_QMONEY_URL_INITIATE=https://uat-adpelite.qmoney.gm/getMoney
PSP_QMONEY_URL_PROCESS=https://uat-adpelite.qmoney.gm/verifyCode
************ Qmoney Payment Service Provider account credential *********************

PSP_QMONEY_NAME=Qmoney 
PSP_QMONEY_ACCOUNT=14001502 
PSP_QMONEY_PIN=1234

******************* Qmoney Api info **************************
QMONEY_API_NAME=Qmoney_token
QMONEY_API_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dnaW5nQXMiOm51bGwsImF1ZCI6WyJBZGFwdGVyX09hdXRoX1Jlc291cmNlX1NlcnZlciJdLCJncmFudF90eXBlIjoicGFzc3dvcmQiLCJkZXZpY2VVbmlxdWVJZCI6bnVsbCwidXNlcl9uYW1lIjoiMTQwMDE1MDIiLCJzY
QMONEY_API_ACCESS_TOKEN_EXPIRY=2023-08-07 14:58:39.136
```
### Obtaining a New Access Token for Qmoney
You can run the following python code to obtain a new access token or extract details from the code and test it in Postman:
```
import requests
import json
from datetime import datetime, timedelta

# Replace placeholders with actual values
auth_url = "<your_auth_url>"
data = {
    "grantType": "<your_grant_type>",
    "username": "<your_username>",
    "password": "<your_password>"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <your_bearer_token>"
}

response = requests.post(auth_url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    response_data = response.json()

    print(response_data)
    new_token = response_data['data']['access_token']
    expiry_seconds = int(response_data['data']['accessTokenExpiry']) - 60
    new_expiry_date = datetime.now() + timedelta(seconds=expiry_seconds)
    print(f'Token = {new_token}')
    print(f'Expiry = {new_expiry_date}')
```
This code will help you generate a new access token for Qmoney your Qmoney integration. Just make sure to replace the placeholders with your actual credentials and endpoint URL.

## Configuration in `openimis-be_py/openIMIS/openIMIS/settings.py`

To integrate Qmoney into your application, add the following code to your `openimis-be_py/openIMIS/openIMIS/settings.py` file:

```python
PSP_QMONEY_GRANTTYPE = os.environ.get('PSP_QMONEY_GRANTTYPE')
PSP_QMONEY_USERNAME = os.environ.get('PSP_QMONEY_USERNAME')
PSP_QMONEY_PASSWORD = os.environ.get('PSP_QMONEY_PASSWORD')
PSP_QMONEY_AUTH_BEARER_TOKEN= os.environ.get('PSP_QMONEY_AUTH_BEARER_TOKEN')

PSP_QMONEY_AUTH_URL = os.environ.get("PSP_QMONEY_AUTH_URL")
PSP_QMONEY_URL_PAYMENT = os.environ.get("PSP_QMONEY_URL_INITIATE")
PSP_QMONEY_URL_PROCESS = os.environ.get("PSP_QMONEY_URL_PROCESS")

PSP_QMONEY_NAME = os.environ.get('PSP_QMONEY_NAME')
PSP_QMONEY_ACCOUNT = os.environ.get('PSP_QMONEY_ACCOUNT')
PSP_QMONEY_PIN = os.environ.get('PSP_QMONEY_PIN')

QMONEY_API_NAME =  os.environ.get('QMONEY_API_NAME')
QMONEY_API_ACCESS_TOKEN = os.environ.get('QMONEY_API_ACCESS_TOKEN')
QMONEY_API_ACCESS_TOKEN_EXPIRY = os.environ.get('QMONEY_API_ACCESS_TOKEN_EXPIRY')
```
This configuration code is necessary to enable Qmoney integration within your application and should be placed in the specified settings file.

## Creating a Payment Service Provider for Qmoney
To set up a Payment Service Provider for Qmoney, we have a test account for receiving payments and a Qmoney wallet number for OTP delivery via email (configurable by Qmoney). Here are the test account details:

The following can be added in your env file before any migration so when you run migration it automatically adds it to your database with you having to add it through the Django Admin
- `name`: Qmoney
- `account`: 14001502
- `pin`: 1234

The following can be added in an insurees detail of insuree_wallet
- `insuree_wallet`: 5811724c

 Please keep in mind that these details are meant for testing purposes. If you intend to transition to a production environment, feel free to update them to align with your production settings.




# Qmoney Mutation Example

#### Initiate Transaction Mutation sample
```
mutation {

    initiateTransaction(input:{
    amount:5.00
    paymentServiceProviderUuid:"5c15ecbd-ef82-40e0-9842-a5a28cedb2b6"
    insureeUuid:"0EFC5C60-AC2E-4F2C-840D-022271005D5A"

    }),{
    responseMessage
    Success
    uuids
    clientMutationId
  }
  }
```

#### Process Transaction Mutation sample

```
mutation {

    processTransaction(input:{
    uuid:"5ff3e97e-f765-413f-929c-6c9044ccaae6"
    amount:5.00
    otp:"364407"
    paymentServiceProviderUuid:"5c15ecbd-ef82-40e0-9842-a5a28cedb2b6"
    insureeUuid:"0EFC5C60-AC2E-4F2C-840D-022271005D5A"
    clientMutationId:""
    }),{

  responseCode
  responseMessage
  clientMutationId
  Success
  detail
  clientMutationId


  }
 
 
  }
```

## Second Workflow 

# Accessing Custom Endpoints

The Mobile Payment module exposes two essential endpoints: `Verify_insuree` and `Process_payment`. These endpoints are designed to be utilized by other payment service providers that wish to enable policyholders to make payments through their services, .

##### Note 
The `Verify_insured` function is designed to display all idle policies that require payment for the insured. On the other hand, the `Process_payment` function manages the payment process by first checking if the policy returned is idle. Subsequently, it verifies whether the payment service provider has returned the expected values before processing the payment.

## Mobile Payment Endpoint Sequence Diagram

![Mobile Payment Endpoint Sequence Diagram](workflow/Mobile_Payemt%20Endpoin%20Sequence%20Diagramt.jpg)

## Configuring Payment Service Providers

When configuring a Payment Service Provider (PSP), it's essential to consider the following:

- If the PSP is a third-party entity that requires access to these endpoints, you should provide the following information during configuration:

  - `psp_name`: The name of the Payment Service Provider.
  - `is_external_api`: This field should be selected when the PSP intends to connect to our endpoint. It indicates that the payment service provider is an external entity requiring access to our services.
  - `interactive_user`: This field represents a foreign key to the OpenIMIS core user models. Selecting an interactive user is crucial to specify the user authorized to make requests to our endpoint.
#### Mutation example
```
mutation{
   createPaymentServiceProvider(input:{
    name:"Afrimoney"
    interactiveUserUuid:"C60E1A15-745A-412F-8A36-A0017ADADCD7"
    isExternalApiUser:true
  }),
  {
    clientMutationId
  }
  }
```
Please make sure to select the `is_external_api` field when you want the Payment Service Provider to connect to our endpoint, and choose an appropriate `interactive_user` to define the user who will be granted the ability to make requests to our endpoint. These configurations are fundamental for effective control and management of access.


## Generating Access Tokens

To enable any Payment Service Provider to make requests to our endpoint, they must be provided with user details and use these details to generate an access token. This access token serves as the key to interact with our endpoint, allowing for secure communication.

It's important to note that the user details should correspond to an interactive user that was created and added during the configuration process when setting up the Payment Service Provider. This interactive user is granted the necessary permissions and serves as the authorized entity for making requests to our endpoint.
sample 
By ensuring that the user details are associated with an interactive user during the PSP configuration, you facilitate the secure generation of access tokens and maintain control over the interactions with our endpoint.

## Mutation Example
**mutation to generate access_token**

```
mutation {
  tokenAuth(username: " enter user name", password: " Enter password"){
    refreshToken
    token
  }
}


```

**Apply the following in the request headers of your graphql_playground**
```
{

  "Authorization": "Bearer your access_token_here"
}
```

**mutation and querys that needs valid_access_token**

#

**Veryfy_inusree quries**

```
query{
  verifyInsuree(chfId:"070707070"){
 
      lastName
      firstName
      message
      policies{
        amount
        status
        productName
        productCode
        token
        
      }
  }
}
 
```

**Process Mutation**
#note json_content field is optional
```
mutation{
   processPayment(inputData:{
    chfId:"070707070",
    amount:""
    pspTransactionId:""
    policy:{
      productName:""
      productCode:""
      token:""  
    },
    jsonExt:"{\" enter here\": \" enter here\"}"
    })
  }
```

