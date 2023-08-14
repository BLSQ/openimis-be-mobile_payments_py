import pathlib
import graphene
import logging
from typing import Optional
from graphene.relay import mutation
from graphene import InputObjectType
from core import filter_validity
from core.schema import OpenIMISMutation
from graphene import relay
from core.utils import TimeUtils
from datetime import date
from core.models import MutationLog
from mobile_payment.apps import MobilePaymentConfig
from .models import Transactions, TransactionMutation, Insuree
from contribution.models import PaymentServiceProvider, Premium, Policy
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
    
    



def reset_transaction_before_update(transaction):
    transaction.amount = None
    transaction.insuree_uuid = None
    transaction.payment_service_provider_uuid =  None
    transaction.status = None
    transaction.transaction_id = None
    transaction.datetime = None


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
    data["PaymentServiceProvider"] = transaction_payment_service_provider
    insuree_uuid = data.pop("insuree_uuid") 
    #fetch insuree_wallet from the databaseand compare it with one inputed in the graphql
    transactioninsuree = Insuree.filter_queryset().filter(uuid=insuree_uuid).first()
    if not transactioninsuree:
        raise Exception (_("wallet_address_not_found") % (insuree_uuid,))
    data["Insuree"] = transactioninsuree
    if transaction_uuid:
        #fetch transactions by uuid
        transaction = Transactions.objects.get(uuid=transaction_uuid)
        [setattr(transaction, key, data[key]) for key in data]
    else:
        #create a new transaction object

        transaction = Transactions.objects.create(**data)
    transaction.save()
    return transaction


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

            payment_service_provider = PaymentServiceProvider.objects.get(uuid=payment_service_provider_uuid)
            if not payment_service_provider :
                raise PermissionDenied (_("invalid payment_service_provider_uuid"))      
            #get wallet_address with existing uuid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            psp_address =payment_service_provider.PSPAccount
            psp_pin = payment_service_provider.Pin
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

class ProcessPaymentInput(graphene.InputObjectType):
    chf_id = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    transaction_id = graphene.String(required = False)

def handle_payment(user, data):
    chf_id = data['chf_id']
    amount = data['amount']
    transaction_id = data['transaction_id']

    try:
        insuree = Insuree.objects.filter(chf_id=chf_id, validity_to__isnull=True).first()
        if not insuree:
            return {"success": False, "message": "Please pass in the correct CH ID."}
    except Insuree.DoesNotExist:
        return {"success": False, "message": "Please pass in the correct CHF ID."}

    policy = Policy.objects.filter(family=insuree.family, status=1).first()
    if policy:
        product = policy.product
        if amount == product.lump_sum:
            premium = Premium.objects.create(amount=amount, policy=policy, pay_date=date.today(), pay_type="Mobile", receipt=transaction_id)
            premium.save()
            update_policy(premium,policy)
            return {'success': True}
        elif amount < product.lump_sum and policy.status == Policy.STATUS_IDLE:
            return {'success': False, 'message': "Amount is too small. It needs to be the exact amount of the product."}
        else:
            return {'success': False, 'message': "Please check again if your policy is already active or has expired. Only policies with idle status can make payment at the moment."}
    else:
        return {"success": False, "message": "The policy you are trying to pay for is either active or expired. Please contact NHIS officer for your registered policies."}



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

            result = handle_payment(info,input_data)
            if result["success"]:
                return "Payment process successful."
            else:
                return result["message"]
        except Exception as exc:
            raise ValidationError("Process failed to work: " + str(exc))
        



