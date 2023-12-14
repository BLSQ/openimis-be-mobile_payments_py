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
from mobile_payment.apps import MobilepaymentConfig
from .models import PaymentTransaction, Insuree, PaymentServiceProvider, ApiRecord, PaymentServiceProviderMutation
from contribution.models import Premium, Policy
from product.models import Product
from graphql_jwt.shortcuts import get_token
from django.utils.translation import gettext_lazy as _
from .api_request import initiate_request, process_request
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError,PermissionDenied
logger = logging.getLogger(__name__)


class PaymentTransactionInputType:
    id = graphene.Int(required=False, read_only= True)
    uuid = graphene.String(required=False)
    amount = graphene.Float()
    payment_service_provider_uuid = graphene.String()
    insuree_uuid = graphene.String()
    status = graphene.Boolean(required=False)
    psp_transaction_id = graphene.String(required=False)
    otp = graphene.String(required = False)
    datetime = graphene.DateTime(required= False)
class PaymentServiceProviderInputType(OpenIMISMutation.Input):
    id = graphene.Int(required = False, read_only = True)
    uuid = graphene.String(required=False)
    account = graphene.String (required=False)
    name = graphene.String(required=True)
    pin = graphene.String(required= False)
    interactive_user_uuid= graphene.String(required= False)
    is_external_api_user = graphene.Boolean(default = False)

def update_or_create_payment_service_provider(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    from core.utils import TimeUtils
    data['validity_from'] = TimeUtils.now()
    interactive_user_uuid = data.pop("interactive_user_uuid") if "interactive_user_uuid" in data else None
    # fetch insuree_wallet from the database and compare it with the one inputed from graphql
    interactive_user = InteractiveUser.filter_queryset().filter(uuid=interactive_user_uuid).first() if interactive_user_uuid else None
    data["interactive_user"] = interactive_user
    # get payment_service_provider from data
    payment_service_provider_uuid = data.pop("uuid") if "uuid" in data else None
    if payment_service_provider_uuid:
        # fetch payment_service_provider from the database and compare it with the one inputed from graphql
        payment_service_provider = PaymentServiceProvider.objects.get(uuid=payment_service_provider_uuid)
        payment_service_provider.save_history()
        [setattr(payment_service_provider , key, data[key]) for key in data]
    else:
        # create new wallet object
        payment_service_provider  = PaymentServiceProvider.objects.create(**data)
    # save record to database
    payment_service_provider.save()
    return payment_service_provider 

def get_object_by_uuid(queryset, uuid, error_message):
    obj = queryset.filter(uuid=uuid).first()
    if not obj:
        raise Exception(error_message % (uuid,))
    return obj

def update_or_create_transaction(data, info):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop("client_mutation_label")
    data['validity_from'] = TimeUtils.now()
    transaction_uuid = data.pop('uuid') if 'uuid' in data else None
    # Get the payment service provider from data from the GraphQL input
    payment_service_provider_uuid = data.pop("payment_service_provider_uuid")
    # Fetch payment service provider from the database
    transaction_payment_service_provider = get_object_by_uuid(
        PaymentServiceProvider.filter_queryset(),
        payment_service_provider_uuid,
        _("payment_service_provider_not_found")
    )
    data["payment_service_provider"] = transaction_payment_service_provider
    # Get the insuree_uuid from data
    insuree_uuid = data.pop("insuree_uuid") 
    # Fetch insuree_wallet from the database
    transaction_insuree = get_object_by_uuid(
        Insuree.filter_queryset(),
        insuree_uuid,
        _("insuree_wallet_address_not_found")
    )
    data["insuree"] = transaction_insuree
    if transaction_uuid:
        # Fetch transactions by uuid
        transaction = PaymentTransaction.objects.get(uuid=transaction_uuid)
        [setattr(transaction, key, data[key]) for key in data]
    else:
        # Create a new transaction object
        transaction = PaymentTransaction.objects.create(**data)
    transaction.save()
    return transaction

class CreatePaymentServiceProvider(OpenIMISMutation):
    """
    Add a payment service provider
    """
    _mutation_module = "mobile_payment"
    _mutation_class = "CreatePaymentServiceProvider"
    class Input(PaymentServiceProviderInputType):
        pass
    @classmethod
    def async_mutate(cls, user, **data)  -> Optional[str]: 
        try:
            #checks if user is authenticated
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                _("mutation.authentication_required"))
            #checks if user has permission to add a payment service provider
            if not user.has_perms(MobilepaymentConfig.gql_mutation_create_payment_service_provider_perms):
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
            if not user.has_perms(MobilepaymentConfig.gql_mutation_update_payment_service_provider_perms):
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
            if not user.has_perms(MobilepaymentConfig.gql_mutation_delete_payment_service_provider_perms):
                raise PermissionDenied(_("unauthorized"))
            
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
             
             # get programs object by uuid
            payment_service_provider = PaymentServiceProvider.objects.get(uuid=data['uuid'])
            payment_service_provider.validity_to = now
            payment_service_provider.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete Wallet. An exception had occured",
                'detail': str(exc)}]
        
class InitiateTransactionMutation(graphene.relay.ClientIDMutation):
    uuids = graphene.String()
    Success = graphene.Boolean()
    responseMessage = graphene.String()
    detail = graphene.String()
    """
    Create a mutation for making a payment transaction
    """
    _mutation_module = "mobile_payment"
    _mutation_class = "InitiateTransactionMutation"
    
    class Input(PaymentTransactionInputType):
        pass
        
    @classmethod
    def mutate_and_get_payload(cls, root, info, **data) -> Optional[str]:
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            if not info.context.user.has_perms(MobilepaymentConfig.gql_mutation_create_payment_transaction_perms):
                raise PermissionDenied(_("unauthorized"))
            client_mutation_id = data.get("client_mutation_id")
            insuree_uuid = data["insuree_uuid"]
            payment_service_provider_uuid = data["payment_service_provider_uuid"]
            amount = data["amount"]
            # Check if the insuree_wallet and wallet_address are valid before sending data to the API
            insuree = get_object_by_uuid(
                Insuree.filter_queryset(),
                insuree_uuid,
                _("invalid insuree_uuid")
            )
            insuree_wallet = insuree.insuree_wallet
            if insuree_wallet is None:
                return InitiateTransactionMutation(responseMessage=_("Insuree wallet does not exist"), Success=False)
            psp = get_object_by_uuid(
                PaymentServiceProvider.objects,
                payment_service_provider_uuid,
                _("invalid payment_service_provider_uuid")
            )
            address = psp.account
            pin = psp.pin
            # Initiate a request for payment
            qmoney_request = initiate_request(insuree_wallet, address, amount, pin)
            if qmoney_request['responseCode'] == '1':
                data['psp_transaction_id'] = qmoney_request['data']['transactionId']
                transaction = update_or_create_transaction(data, info)
                return InitiateTransactionMutation(uuids=transaction.uuid, Success=True, responseMessage=_("Success"))
            else:
                raise Exception(_("Failed to initiate payment"))
        except Exception as exc:
            logger.exception("transaction.mutation.failed_to_create_initiate_transaction")
            return InitiateTransactionMutation(
                responseMessage=_("transaction.mutation.failed_to_create_initiate_transaction"), 
                detail=str(exc), 
                Success=False
            )
        
class ProcessTransactionMutation(graphene.relay.ClientIDMutation):
    """
    create a mutation to update a payment transaction
    """
    _mutation_module = "mobile_payment"
    _mutation_class = "ProcessTransactionMutation"
    
    class Input(PaymentTransactionInputType):
        pass
    
    responseMessage = graphene.String()
    responseCode = graphene.String()
    Success = graphene.Boolean()
    detail = graphene.String()
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            if not info.context.user.has_perms(MobilepaymentConfig.gql_mutation_update_payment_transaction_perms):
                raise PermissionDenied(_("unathorized"))
            client_mutation_id = data.get("client_mutation_id")
            transaction_uuid = data['uuid']
            transacton = PaymentTransaction.objects.get(uuid=transaction_uuid)
            if not transacton:
                raise PermissionDenied(_("invalid transaction_uuid"))
            transaction_id = transacton.psp_transaction_id
            otp = data['otp']
            logger.info(f'Transaction_id = {transaction_id}')
            logger.info(f'otp = {otp}')
            qmoney_process = process_request(otp, transaction_id)
            if qmoney_process['responseCode'] == '1':
                data['status'] = True
                update_or_create_transaction(data, info)
                return ProcessTransactionMutation(responseCode='1', responseMessage='Success', Success=True)
            elif qmoney_process['responseCode'] == '-120008':
                return ProcessTransactionMutation(responseCode='-120008', responseMessage="Insufficent Balance in your Qmoney wallet", Success=False)
            else:
                return ProcessTransactionMutation(responseCode=int(qmoney_process['responseCode']), responseMessage=qmoney_process["responseMessage"], Success=False)
        except Exception as exc:
            logger.exception("transaction.mutation.failed_to_update_process_transaction")
            return ProcessTransactionMutation(responseCode='0', 
                                              responseMessage=_("transaction.mutation.failed_to_update_process_transaction"), 
                                              detail=str(exc), 
                                              Success=False
                                            )
# ***********************************Endpoint Process_Payment***********************************           
class ProductInput(graphene.InputObjectType):
    product_name = graphene.String(required=True)
    product_code = graphene.String(required=True)
    token = graphene.String(required = True)
class ProcessPaymentInput:
    chf_id = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    psp_transaction_id = graphene.String(required = True)
    psp_service_provider_uuid = graphene.String(required = False)
    policy = graphene.Field( ProductInput, required = True)
    audit_user_id = graphene.Int(required = False) #user_id_for_audit
    json_ext = graphene.types.json.JSONString(required=False)

def handle_payment(user, data):
    chf_id = data['chf_id']
    amount = data['amount']
    psp_transaction_id = data['psp_transaction_id']
    psp_service_provider_uuid = data['psp_service_provider_uuid']
    product_name = data['policy']['product_name']
    product_code = data['policy']['product_code']
    token = data['policy']['token']
    audit_user_id = data['audit_user_id']
    json_content = json.dumps(data.get('json_ext', []))


    try:
        insuree = Insuree.objects.filter(chf_id=chf_id, validity_to__isnull=True).first()
        if not insuree:
            return {"success": False, "message": "Please pass in the correct CH ID."}
    except Insuree.DoesNotExist:
        return {"success": False, "message": "Please pass in the correct CHF ID."}

    
    policy = Policy.objects.filter(family=insuree.family, uuid=token, validity_to__isnull=True).first()
    if policy:
        product = policy.product
        if (
            amount == product.lump_sum
            and policy.status == Policy.STATUS_IDLE
            and product_name == product.name
            and product_code == product.code
        ):
            psp_service_provider = PaymentServiceProvider.filter_queryset().filter(uuid=psp_service_provider_uuid).first()
            if not psp_service_provider:
                raise ValidationError("You are not authorized to perform this operation")
            transaction = PaymentTransaction.objects.create(amount=amount, payment_service_provider=psp_service_provider, status=1, psp_transaction_id = psp_transaction_id, json_content=json_content, datetime=date.today())
            transaction.save()
            premium = Premium.objects.create(amount=transaction.amount, policy=policy, pay_date=date.today(), pay_type="M", payment_transaction=transaction, audit_user_id =audit_user_id)
            premium.save()
            update_policy(premium, policy)
            return {'success': True}
        elif amount < product.lump_sum and policy.status == Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Amount is too small. It needs to be the exact amount of the product."}
        elif amount > product.lump_sum and policy.status == Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Amount is too large. pls enter the exact amount the product cost."}
        elif amount == product.lump_sum and policy.status != Policy.STATUS_IDLE and product_name == product.name and product_code == product.code:
            return {'success': False, 'message': "Please check again if your policy you are trying to pay for is idle  or active."}
    else:
        return {"success": False, "message": "Unable to process payment. insuree does not have any idle policy that requires payment."}
        
def update_policy(premium, policy):
    policy.status = Policy.STATUS_ACTIVE
    policy.effective_date = premium.pay_date if premium.pay_date > policy.start_date else policy.start_date
    policy.save()

class ProcessPaymentMutation(graphene.relay.ClientIDMutation):
    Success = graphene.Boolean()
    responseMessage = graphene.String()
    detail = graphene.String()

    class Input(ProcessPaymentInput):
        pass
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        try:
            if info.context.user is AnonymousUser:
                raise ValidationError(_("mutation.authentication_required"))
            username = info.context.user.username
            audit_user_id = info.context.user.id_for_audit
            try:
                psp = PaymentServiceProvider.objects.filter(interactive_user__login_name=username, is_external_api_user=True).first()
                if not psp:
                    raise ValidationError("You are not authorized to perform this operation")
            except PaymentServiceProvider.DoesNotExist:
                raise ValidationError("You are not authorized to perform this operation")
            data['psp_service_provider_uuid'] = psp.uuid
            data['audit_user_id'] = audit_user_id
            result = handle_payment(info,data)
            logger.info(data)
            api_record = ApiRecord.objects.create(request_date=data, response_date=result)
            api_record.save()
            if result["success"]:
                return ProcessPaymentMutation(
                    Success=True,
                    responseMessage="Payment processed successfully",  
                )
            else:
                return ProcessPaymentMutation(
                    Success=False,
                    responseMessage=result["message"],  
                )
        except Exception as exc:
            return ProcessPaymentMutation(
                Success=False,
                responseMessage="Process failed to work",
                detail = str(exc)
            )