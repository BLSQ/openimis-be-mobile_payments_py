# openIMIS Backend Claim reference module
This repository holds the files of the openIMIS Backend payment reference module.

**Note**
```
To generate an access token, you need to create an interactive user and assign the necessary permissions for the specific actions you want to perform. Additionally, assign a payment service provider to the interactive user for it to work properly. The recommended way to assign an interactive user is through the Django Admin interface, where you can also manage permissions effectively.For now use the defualt interactive user detail to generate access_token
```

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
        
      }
  }
}
 
```

**Process Mutation**

```
mutation{
   processPayment(inputData:{
    chfId:"070707070",
    amount:"10000"
    pspServiceProvider:"2d6c1d66-661a-4073-a44c-0b8e0987927"
    
    
  })
  }
```

