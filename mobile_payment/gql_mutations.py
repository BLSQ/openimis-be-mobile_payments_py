import pathlib
import graphene
import json
import graphql_jwt
import logging
from typing import Optional
from graphene.relay import mutation
from core import filter_validity
from core.schema import OpenIMISMutation
from core.utils import TimeUtils
from core.models import InteractiveUser
from datetime import date
from mobile_payment.apps import MobilePaymentConfig
from .models import Transactions, Insuree, PaymentServiceProvider, Api_Records
from contribution.models import Premium, Policy
from product.models import Product
from graphql_jwt.shortcuts import get_token
from django.utils.translation import gettext_lazy as _
from .api_request import initiate_request, process_request
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError,PermissionDenied
logger = logging.getLogger(__name__)




class APIutilities:
    id = graphene.Int(required= False, read_only = True)
    name = graphene.String(required= False)
    access_token = graphene.String(required=False)
    access_TokenExpiry= graphene.DateTime(graphen=False)

class TransactionBase:
    
    id = graphene.Int(required=False, read_only= True)
    uuid = graphene.String(required=False)
    amount = graphene.Float()
    payment_service_provider_uuid = graphene.String()
    insuree_uuid = graphene.String()
    status = graphene.Boolean(required=False)
    transaction_id = graphene.String(required=False)
    otp = graphene.String(required = False)
    datetime = graphene.DateTime(required= False)
    
class PaymentServiceProviderInputType(OpenIMISMutation.Input):
    id = graphene.Int(required = False, read_only = True)
    uuid = graphene.String(required=False)
    psp_account = graphene.String (required=False)
    psp_name = graphene.String(required=True)
    psp_pin = graphene.String(required= False)
    interactive_user_uuid= graphene.String(required= False)
    is_external_api_user = graphene.Boolean(default = False)
    
def reset_payment_service_provider_before_udate(payment_service_provider):
    payment_service_provider.psp_name = None
    payment_service_provider.psp_account = None
    payment_service_provider.psp_pin = None
    
def reset_transaction_before_update(transaction):
    transaction.amount = None
    transaction.insuree_uuid = None
    transaction.payment_service_provider_uuid =  None
    transaction.status = None
    transaction.transaction_id = None
    transaction.datetime = None
    
def update_or_create_payment_service_provider(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    from core.utils import TimeUtils
    data['validity_from'] = TimeUtils.now()
    interactive_user_uuid = data.pop("interactive_user_uuid") if "" in data else None
    # fetch insuree_wallet from the database and compare it with the one inputed from graphql
    interactive_user = InteractiveUser.filter_queryset().filter(uuid=interactive_user_uuid).first()
    data["interactive_user"] = interactive_user
    # get wallet_uuid from data
    Payment_service_provider_uuid = data.pop("uuid") if "uuid" in data else None
    if Payment_service_provider_uuid:
        # fetch wallet by uuid
        payment_service_provider = PaymentServiceProvider.objects.get(uuid=Payment_service_provider_uuid)
        payment_service_provider.save_history()
        [setattr(payment_service_provider , key, data[key]) for key in data]
    else:
        # create new wallet object
        payment_service_provider  = PaymentServiceProvider.objects.create(**data)
    # save record to database
    payment_service_provider.save()
    return payment_service_provider 


def update_or_create_transaction(data, info):
    #check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    #check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop("client_mutation_label")
    data['validity_from'] = TimeUtils.now()
 
    transaction_uuid = data.pop('uuid') if 'uuid' in data else None
    # get the wallet_address                                                                        from the graphql input
    payment_service_provider_uuid = data.pop("payment_service_provider_uuid")
    # fetch insuree_wallet from the database and compare it with the one inputed from graphql
    transaction_payment_service_provider = PaymentServiceProvider.filter_queryset().filter(uuid=payment_service_provider_uuid).first()
    #checks if the wallet inputed exist in the databse if not it raise exception of not found
    if not transaction_payment_service_provider:
        raise Exception (_("wallet_address_not_found") % (payment_service_provider_uuid,))
    #gets the insuree_wallet
    data["payment_service_provider"] = transaction_payment_service_provider
    insuree_uuid = data.pop("insuree_uuid") 
    #fetch insuree_wallet from the databaseand compare it with one inputed in the graphql
    transactioninsuree = Insuree.filter_queryset().filter(uuid=insuree_uuid).first()
    if not transactioninsuree:
        raise Exception (_("wallet_address_not_found") % (insuree_uuid,))
    data["insuree"] = transactioninsuree
    if transaction_uuid:
        #fetch transactions by uuid
        transaction = Transactions.objects.get(uuid=transaction_uuid)
        [setattr(transaction, key, data[key]) for key in data]
    else:
        #create a new transaction object

        transaction = Transactions.objects.create(**data)
    transaction.save()
    return transaction

class CreatePaymentServiceProvider(OpenIMISMutation):
    """
    Add a Merchant wallet address for mobile money payment
    """
    _mutation_module = "mobile_payment"
    _mutation_class = "CreatePaymentServiceProvider"

    class Input(PaymentServiceProviderInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data)  -> Optional[str]: 
        try:
            
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                _("mutation.authentication_required"))
            #checks if user has permission to create a wallet
            if not user.has_perms(MobilePaymentConfig.gql_mutation_create_paymnet_service_provider):
                raise PermissionDenied(_("unauthorized"))
            client_mutation_id = data.get("client_mutation_id")
            # it create data inputs from the premium graphql
            payment_service_provider = update_or_create_payment_service_provider(data, user)
            PaymentServiceProviderMutation.object_mutated(user, client_mutation_id=client_mutation_id, payment_service_provider=payment_service_provider)
            return None
        except Exception as exc:
            logger.debug("Exception when deleting premium %s", exc_info=exc)
            return [{
                'message': _("wallet.mutation.failed_to_create_wallet"),
                'detail': str(exc)}
            ]


class UpdatePaymentServiceProvider(OpenIMISMutation):
    _mutation_module = "mobile_payment"
    _mutation_class = "UpdatePaymentServiceProvider"


    class Input (PaymentServiceProviderInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):

        try:
            if not user.has_perms(MobilePaymentConfig.gql_mutation_update_paymnet_service_provider):
                raise PermissionDenied(_("unauthorized"))
            #get merchant uuid
            payment_service_provider_uuid = data.pop('uuid')
            if payment_service_provider_uuid:
                #fetch merchnat uuid from database
                payment_service_provider = PaymentServiceProvider.objects.get(uuid = payment_service_provider_uuid)
                [setattr(payment_service_provider, key, data[key]) for key in data]
            else:
                 #raise an error if uuid is not valid or does not exist
                 raise PermissionDenied(_("unauthorized"))
            #saves update dta
            payment_service_provider.save()
            return None
        except Exception as exc:
            return [{
                
                'message': _("wallet.mutation.failed_to_update_wallet"),
                'detail': str(exc)}]


class DeletePaymentServiceProvider(OpenIMISMutation):

    _mutation_module = 'mobile_payment'
    _mutation_class = 'DeletePaymentServiceProvider'


    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):

        try:
             # Check if user has permission
            if not user.has_perms(MobilePaymentConfig.gql_mutation_delete_paymnet_service_provider):
                raise PermissionDenied(_("unauthorized"))
            
             # get programs object by uuid
            payment_service_provider = PaymentServiceProvider.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            payment_service_provider.validity_to = now
            payment_service_provider.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete Wallet. An exception had occured",
                'detail': str(exc)}]


class  InitiateTransactionMutation(OpenIMISMutation):

    uuids = graphene.String()
    """
    create a mutaion for making a trasaction
    """
    _mutation_module = "mobile_payment"
    _mutation_class = "InitiateTransactionMutation"
    
    class Input(TransactionBase, OpenIMISMutation.Input):
         pass
    @classmethod
    def mutate_and_get_payload(cls, root, info, **data) -> Optional[str]:
        response = super().mutate_and_get_payload(root, info, **data)
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            if not info.context.user.has_perms(MobilePaymentConfig.gql_mutation_create_transaction_perms):
                raise PermissionDenied(_("unathorized"))
            client_mutation_id = data.get("client_mutation_id")
            insuree_uuid = data["insuree_uuid"]
            payment_service_provider_uuid = data["payment_service_provider_uuid"]
            amount  = data["amount"]
            
            #check if the the insuree_wallet and wallet_address is valid before sending datato the api
            
            insuree = Insuree.filter_queryset().filter(uuid=insuree_uuid).first()           
            if not insuree:
                raise PermissionDenied (_("invalid insuree_uuid"))
            #get insuree_wallet with existing uuid
            insuree_wallet = insuree.insuree_wallet

            psp = PaymentServiceProvider.objects.get(uuid=payment_service_provider_uuid)
            if not psp :
                raise PermissionDenied (_("invalid payment_service_provider_uuid"))      
            #get wallet_address with existing uuid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            psp_address = psp.psp_account
            psp_pin = psp.psp_pin
            #Initiate a request for payment
            Qcell_request = initiate_request(insuree_wallet,psp_address,amount,psp_pin,)
            if Qcell_request['responseCode'] == '1':
                data['transaction_id'] = Qcell_request['data']['transactionId']
                transaction = update_or_create_transaction(data, info)
            else:
                raise Exception(_("Failed to initiate payment"))
            return InitiateTransactionMutation(uuids=transaction.uuid, internal_id=response.internal_id)
        except Exception as exc:
            logger.exception("transaction.mutation.failed_to_create_transaction")
            return [{
                    'message': _("transaction.mutation.failed_to_create_transaction"),
                    'detail': str(exc)}] 
        
    
        
class  ProcessTransactionMutation(OpenIMISMutation):
    """
    create a mutaion for making a trasaction
    """

    _mutation_module = "mobile_payment"
    _mutation_class = "ProcessTransactionMutation"

    class Input(TransactionBase, OpenIMISMutation.Input):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data) -> Optional[str]:
        response = super().mutate_and_get_payload(root, info, **data)
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            if not info.context.user.has_perms(MobilePaymentConfig.gql_mutation_create_transaction_perms):
                raise PermissionDenied(_("unathorized"))
            client_mutation_id = data.get("client_mutation_id")
            transaction_uuid = data['uuid']
            transacton = Transactions.objects.get(uuid=transaction_uuid )
            if not transacton:
                raise PermissionDenied (_("invalid transaction_uuid"))
            transaction_id = transacton.transaction_id
            otp = data['otp']
            print(f' Transaction_id = {transaction_id}')
            print (f'otp =  {otp}')
            Qcell_process = process_request(otp, transaction_id)
            if Qcell_process['responseCode'] == '1':
                data['status'] = True
                update_or_create_transaction(data, info)
            else:
                raise Exception(_("Failed to initiate payment"))
            return ProcessTransactionMutation(internal_id=response.internal_id)
        except Exception as exc:
            logger.exception("transaction.mutation.failed_to_process_transaction")
            return [{
                    'message': _("transaction.mutation.failed_to_process_transaction"),
                    'detail': str(exc)}]

# *********************************** Afri Money ***********************************           
class ProductInput(graphene.InputObjectType):
    product_name = graphene.String(required=True)
    product_code = graphene.String(required=True)
    token = graphene.String(required = True)
class ProcessPaymentInput(graphene.InputObjectType):
    chf_id = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    transaction_id = graphene.String(required = False)
    psp_service_provider_uuid = graphene.String(required = False)
    policy = graphene.Field( ProductInput, required = False)
    json_content = graphene.JSONString()

def handle_payment(user, data):
    chf_id = data['chf_id']
    amount = data['amount']
    psp_service_provider_uuid = data['psp_service_provider_uuid']
    product_name = data['policy']['product_name']
    product_code = data['policy']['product_code']
    token = data['policy']['token']
    json_content = json.dumps(data.get('json_content', []))
    
    

    try:
        insuree = Insuree.objects.filter(chf_id=chf_id, validity_to__isnull=True).first()
        if not insuree:
            return {"success": False, "message": "Please pass in the correct CH ID."}
    except Insuree.DoesNotExist:
        return {"success": False, "message": "Please pass in the correct CHF ID."}

    
    policy = Policy.objects.filter(family=insuree.family, uuid=token).first()
    if policy:
        product = policy.product
        if (
            amount == product.lump_sum
            and policy.status == Policy.STATUS_IDLE
            and product_name == product.name
            and product_code == product.code
        ):
            psp_service_provider = PaymentServiceProvider.objects.get(uuid=psp_service_provider_uuid)
            transactions = Transactions.objects.create(amount=amount, payment_service_provider=psp_service_provider, status=1, json_content=json_content)
            transactions.save()
            premium = Premium.objects.create(amount=amount, policy=policy, pay_date=date.today(), pay_type="Mobile", transaction=transactions)
            premium.save()
            update_policy(premium, policy)
            return {'success': True}
        elif amount < product.lump_sum and policy.status == Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Amount is too small. It needs to be the exact amount of the product."}
        elif amount > product.lump_sum and policy.status == Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Amount is too large. pls enter the excatt amount the product cost."}
        elif amount == product.lump_sum and policy.status != Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Please check again if your policy you are trying to pay for is idle  or active."}
        else:
            return {'success': False, 'message': "Please check again if your the policy is already active or has expired. Only policies with idle status can make payment at the moment."}
    else:
        return {"success": False, "message": "insuree does not have polciy contact NHIS for more information."}
        
def update_policy(premium, policy):
    policy.status = Policy.STATUS_ACTIVE
    policy.effective_date = premium.pay_date if premium.pay_date > policy.start_date else policy.start_date
    policy.save()

class ProcessPayment(graphene.Mutation):
    class Arguments:
        input_data = ProcessPaymentInput(required=True)

    Output = graphene.String

    @staticmethod
    def mutate(root, info, input_data=None):
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            
            username = info.context.user.username
            psp = PaymentServiceProvider.objects.get(interactive_user__login_name=username,  is_external_api_user=True)
            if not psp:
                raise ValidationError(
                "You are not authorized to perform this operation")
        
            input_data['psp_service_provider_uuid'] = psp.uuid
            print(input_data)
            result = handle_payment(info,input_data)
            api_record = Api_Records.objects.create(request_date=input_data, response_date=result)
            api_record.save()
            if result["success"]:
                return "Payment process successful."
            else:
                return result["message"]
        except Exception as exc:
            api_record = Api_Records.objects.create(request_date=input_data, response_date=str(exc))
            api_record.save()
            raise ValidationError("Process failed to work: " + str(exc))

