## openIMIS Backend Mobile_Payment Modoule
This repository holds the files of the openIMIS Backend payment reference module.


The Mobile Payment module is designed to enable seamless payment processing for insured policies. This module comprises two distinct workflows:

1. **Integration with Qmoney**: In this workflow, the module establishes a connection with the Qmoney payment service provider, facilitating secure and efficient payment processing for policyholders.

2. **Endpoint Exposition**: The module also exposes two essential endpoints, `Verify_insuree` and `Process_payment`. These endpoints can be utilized by other payment service providers seeking to offer policyholders the ability to make payments through their services. This flexibility allows for easy integration with a variety of payment providers, making it a versatile solution for policyholder payments.

Qmoney implementation includes a frontend in the contrubution module of FE link: [openimis-fe-contribution_js](https://github.com/BLSQ/openimis-fe-contribution_js/tree/develop).

"Link to the workflow diagram and database of the Mobile Payment module can be found here [workflow](https://github.com/BLSQ/openimis-be-mobile_payments_py/tree/feature/gambia/workflow)


# Qmoney Integration Guide

Qmoney provides two essential mutations: `InitiateTransactionMutation` and `ProcessTransactionMutation`. These mutations enable seamless payment processing between accountants and insured individuals.

## Initiating a Transaction

To initiate a transaction, an accountant is required to select the following fields:
- `amount`
- `paymentServiceProviderUuid`
- `insureeUuid`

Upon selection, an OTP is generated and sent to the insuree's phone number. The insuree is responsible for sharing this OTP with the accountant. The accountant will then enter the OTP to proceed with the transaction.

## Processing a Transaction

When processing a transaction, the following fields are required:
- `uuid`
- `otp`
- `amount`
- `insureeUuid`
- `paymentServiceProvider`

Once a transaction is initiated and successfully processed, it is added to the contribution table named "premium." The transaction details are stored by adding the transaction UUID to the "transaction_uuid" field, which acts as a foreign key.

### Note

For an insuree to receive an OTP, their Qmoney wallet information must be saved in the "insuree_wallet" field of the Insuree model. The status of a transaction is initially set to `0` when initiated and changes to `1` upon successful processing.


# Qmoney Testing Setup

Before you can begin testing with Qmoney, you need to configure the following variables in your `openimis-be_py/.env` file:

```env
PSP_QMONEY_GRANTTYPE=<Grant Type>
PSP_QMONEY_USERNAME=<Authentication Username for Authorization>
PSP_QMONEY_PASSWORD=<Password for Authentication>
PSP_QMONEY_AUTH_URL=<URL for Authentication and Access Token Generation>
PSP_QMONEY_URL_INITIATE=<URL for Initiating Money Transfer>
PSP_QMONEY_URL_PROCESS=<URL for Verifying Money Transfer
```
Ensure that you replace the placeholders <Grant Type>, <Authentication Username for Authorization>, and other placeholders with the actual values specific to your Qmoney configuration.

These settings are crucial for creating a successful testing environment when working with Qmoney integration.

### Test use case sample
```
PSP_QMONEY_GRANTTYPE=password
PSP_QMONEY_USERNAME=14001502
PSP_QMONEY_PASSWORD=Nhia@123
PSP_QMONEY_AUTH_URL=https://uat-adpelite.qmoney.gm/login
PSP_QMONEY_URL_INITIATE=https://uat-adpelite.qmoney.gm/getMoney
PSP_QMONEY_URL_PROCESS=https://uat-adpelite.qmoney.gm/verifyCode
```


## Configuration in `openimis-be_py/openIMIS/openIMIS/settings.py`

To integrate Qmoney into your application, add the following code to your `openimis-be_py/openIMIS/openIMIS/settings.py` file:

```python
PSP_QMONEY_AUTH_URL = os.environ.get("PSP_QMONEY_AUTH_URL")
PSP_QMONEY_GRANTTYPE = os.environ.get('PSP_QMONEY_GRANTTYPE')
PSP_QMONEY_USERNAME = os.environ.get('PSP_QMONEY_USERNAME')
PSP_QMONEY_PASSWORD = os.environ.get('PSP_QMONEY_PASSWORD')
PSP_QMONEY_URL_PAYMENT = os.environ.get("PSP_QMONEY_URL_INITIATE")
PSP_QMONEY_URL_PROCESS = os.environ.get("PSP_QMONEY_URL_PROCESS")
```
This configuration code is necessary to enable Qmoney integration within your application and should be placed in the specified settings file.

## Creating a Payment Service Provider for Qmoney

To facilitate integration with Qmoney, we've been provided with a test account that allows us to receive money. Below are the test account details:

- `psp_name`: Qmoney
- `psp_account`: 14001502
- `psp_pin`: 1234

These details have been included in our migration file. When you run the migration, it will automatically create the Payment Service Provider for Qmoney using the provided test account details. Please note that these details are intended for testing purposes, and if you plan to move to a production environment, you can update them accordingly to reflect the production configuration.

### Add Qmoney Access Token

In order to make requests to any of the Qmoney endpoints, you need an access token. The generation of the access token is already handled in the code, and all you have to do is add the following details in the `Api_utlity` model:

- `name`: Qcell_token
- `access_token`: `<generated access_token>`
- `access_TokenExpiry`: `<access_token expiry date, e.g., 2023-08-07 14:58:39.136>`

For Qmoney integration, the initial access token details are added during the migration process. If you are planning to transition to a production environment, you can choose to update the access_token field and the expiry date as needed. It's important to note that if the access token expires, the system automatically sends a new request to update the access token field. For more details on the implementation, you can refer to `mobile_payment/utils.py`.

# Qmoney Mutation Example

#### Initiate Transaction Mutation sample
```
mutation {
    initiateTransaction(input:{
    amount:5.00
    paymentServiceProviderUuid:"f6212ae6-ec92-46fc-92fd-a227bdb4e0d9"
    insureeUuid:"CC308EC4-E8D6-4BC4-B8C8-9D7F7079AA48"
    }),{
    internalId
    uuids
    clientMutationId
    
    
    
  }


  }
```

#### Process Transaction Mutation sample

```
mutation {
    processTransaction(input:{
    uuid:"031889a2-1def-4a89-a928-6eb56334da80"
    amount:5.00
    otp:"213"
    paymentServiceProviderUuid:"f6212ae6-ec92-46fc-92fd-a227bdb4e0d9"
    insureeUuid:"CC308EC4-E8D6-4BC4-B8C8-9D7F7079AA48"
    }),{
    internalId
    clientMutationId
    
    
    
  }


  }
```
# Accessing Custom Endpoints

The Mobile Payment module exposes two essential endpoints: `Verify_insuree` and `Process_payment`. These endpoints are designed to be utilized by other payment service providers that wish to enable policyholders to make payments through their services.

## Configuring Payment Service Providers

When configuring a Payment Service Provider (PSP), it's essential to consider the following:

- If the PSP is a third-party entity that requires access to these endpoints, you should provide the following information during configuration:

  - `psp_name`: The name of the Payment Service Provider.
  - `is_external_api`: This field should be selected when the PSP intends to connect to our endpoint. It indicates that the payment service provider is an external entity requiring access to our services.
  - `interactive_user`: This field represents a foreign key to the OpenIMIS core user models. Selecting an interactive user is crucial to specify the user authorized to make requests to our endpoint.

Please make sure to select the `is_external_api` field when you want the Payment Service Provider to connect to our endpoint, and choose an appropriate `interactive_user` to define the user who will be granted the ability to make requests to our endpoint. These configurations are fundamental for effective control and management of access.


## Generating Access Tokens

To enable any Payment Service Provider to make requests to our endpoint, they must be provided with user details and use these details to generate an access token. This access token serves as the key to interact with our endpoint, allowing for secure communication.

It's important to note that the user details should correspond to an interactive user that was created and added during the configuration process when setting up the Payment Service Provider. This interactive user is granted the necessary permissions and serves as the authorized entity for making requests to our endpoint.

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
    amount:"10000"
    policy:{
      productName:"Basic Cover Ultha"
      productCode:"BCUL0001"
      token:"2929BD6A-FDFA-42B7-9EF5-11935F0ED846"  
    },
    jsonContent:"{\"fee\": 100}"
    })
  }
```

