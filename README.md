## openIMIS Backend Mobile_Payment Modoule
This repository holds the files of the openIMIS Backend payment reference module.


The Mobile Payment module is designed to enable seamless payment processing for insured policies. This module comprises two distinct workflows:

1. **Integration with Qmoney**: In this workflow, the module establishes a connection with the Qmoney payment service provider, facilitating secure and efficient payment processing for policyholders.

2. **Endpoint Exposition**: The module also exposes two essential endpoints, `Verify_insuree` and `Process_payment`. These endpoints can be utilized by other payment service providers seeking to offer policyholders the ability to make payments through their services. This flexibility allows for easy integration with a variety of payment providers, making it a versatile solution for policyholder payments.

Please refer to the documentation for further information on using and configuring this module.


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


#Qmoney Mutation Examole

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
### step to test Qmoney from Graphql Play Ground

add

## Afrimoney Setup test Mutation 
The Afrimoney has two endpoint which is  ` verifyInsuree ` and ` processPayment ` this endpoints can only be accessed by an interactive_user that is selected in the process of a creating a payment serivce provider.


* Create a PaymentServiceProvider: You Can Create a Payment Service Provider from the django admin, the following needs to be considered if creating a payment servive provider 
  - if the payment service provider is a third party that needs to access our api endpoint then thefollowing  fileds needs to be added ` psp_name ` , ` is_externapi ` ` interactive_user ` note if the field is_externapi and interactive_useris not selected,then both endpoint wont be accessible.

  - if the payment serivice provider requires we connect to their endpoint then the following field can be considered `psp_name`, ` psp_account ` ,  ` psp_pin ` however other fields could be added as well if it is not on the payment_service_provider model.
  Note other changes and codes needs to be written by the developer

* Generate an access_tooken: To generate an acess_token you need to use  the username and passowrd of the interactive user that was selected when creating a paymentserviceprovider in the django admin all mutation are provided below.

**Note**
<table align="center"><tr><td>To generate an access token, you need to create an interactive user and assign the necessary permissions for the specific actions you want to perform. Additionally, assign a payment service provider to the interactive user for it to work properly. The recommended way to assign an interactive user is through the Django Admin interface, where you can also manage permissions effectively.For now use the defualt interactive user detail to generate access_token</td></tr></table>


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

