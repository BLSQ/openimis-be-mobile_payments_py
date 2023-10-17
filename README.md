## openIMIS Backend Mobile_Payment Modoule
This repository holds the files of the openIMIS Backend payment reference module.

## Qmoney Setup and Mutation

<table align="center"><tr><td>Qmoney has the following mutations which is ` InitiateTransactionMutation` and ` ProcessTransactionMutation ` an accountant needs to initatiate a transaction by selecting the following fields ` amount `, ` paymetServiceProviderUuid`, `insureeUuid ` then the insuree will then receive an otp whcih will be sent to his phone number and share that otp with the accountant whcich will be enetred by the accountanct to process the transaction. The follwing fields are entered in the ProcessTransaction ` uuid `,  ` otp `, ` amount ` ` insureeUuid` and  ` paymentServiceProvider`. 

### Note
For an Insuree to receicve an OTP he or she needs to have a qmnoey wallet informaion saved the in the  ` insuree_wallet ` field of the insuree model. When a transaction is initiated  the status is Zero  until transaction is successfuly processed it is changed to 1.
</td></tr></table>


The Qmoney needs the following setup before testing  

* add the following code in ` openimis-be_py/.env `

```
GRANTTYPE=password
USERNAME=14001502
PASSWORD=Nhia@123
QCELL_AUTH_URL=https://uat-adpelite.qmoney.gm/login
QCELL_URL_INITIATE=https://uat-adpelite.qmoney.gm/getMoney
QCELL_URL_PROCESS=https://uat-adpelite.qmoney.gm/verifyCode

```

* add the following code in your ` openimis-be_py/openIMIS/openIMIS/settings.py `

```
QCELL_AUTH_URL = os.environ.get("QCELL_AUTH_URL")
GRANTTYPE = os.environ.get('GRANTTYPE')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
QCELL_URL_PAYMENT = os.environ.get("QCELL_URL_INITIATE")
QCELL_URL_PROCESS = os.environ.get("QCELL_URL_PROCESS")
```

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

