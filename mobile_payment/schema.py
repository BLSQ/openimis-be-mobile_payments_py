from django.conf import settings
import graphene
from core.schema import OrderedDjangoFilterConnectionField,OpenIMISMutation, signal_mutation_module_validate
from graphene_django.filter import DjangoFilterConnectionField
from mobile_payment.models import Transactions,TransactionMutation
from django.dispatch import Signal
from django.db.models import Q
import graphene_django_optimizer  as gql_optimizer
from .apps import MobilePaymentConfig
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _
from .gql_queries import *
from .gql_mutations import *



class Query(graphene.ObjectType):
    verify_insuree = graphene.Field(
        VerifyGQLtype,
        chf_id=graphene.String(required=True),
    )
    def resolve_verify_insuree(self, info, chf_id=None):
        try:
            insuree = Insuree.objects.filter(chf_id=chf_id, validity_to__isnull=True).first()
            if not insuree:  
                 return CustomMessagetype(
                    message="chf_id does not exist"

                 )                                                                          
        except Insuree.DoesNotExist:
            return CustomMessagetype(
                message="chf_id does not exist",
            )
        policys= Policy.objects.filter(family=insuree.family, validity_to__isnull=True).all()
        policies_list = []
        for policy in policys:
            policies_list.append({
                "product_name": policy.product.name,
                "amount": policy.product.lump_sum,  
                "status": policy.status                                         
            })
        policie = Policy.objects.filter(family=insuree.family, validity_to__isnull=True).first()
        if not policie:
            # If policy does not exist for the family_id, return only the 'message' field
            return VerifyGQLtype(
                message="policy does not exist",
            )
        
        else:                                                      
            # If status is 8, return only the 'message' field
            return VerifyGQLtype(
                first_name=insuree.other_names,
                last_name=insuree.last_name,
                policies=policies_list,
                message="1 for idle, 2is for active",
            )
    transactions = OrderedDjangoFilterConnectionField(
        TransactionsGQLType,
        order_by=graphene.List(of_type=graphene.String),
        show_hsitory = graphene.Boolean(),
        client_mutation_id = graphene.String()
    )

    transactionStr = OrderedDjangoFilterConnectionField(
        TransactionsGQLType,
        str = graphene.String(),
        
    )



    def resolve_transaction(self, info, **kwargs):
        """
        Extra steps to perform when schema is Required
        """
        #check if the user has permission
        if not info.context.user.has_perms(MobilePaymentConfig.gql_query_transactions_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
            
        show_hsitory = kwargs.get('show_history', False)
        if not show_hsitory:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get('client_mutation_id', None)
        if client_mutation_id:
            filters.append( Q(mutations__mutation__client_mutation_id=client_mutation_id) )

        return gql_optimizer.query(Transactions.objects.filter(*filters).all(), info)
    
    def resolve_transactionStr(self, info, **kwargs):
        """
        Extra steps to perform when schema is Required
        """
        #check if the user has permission
        if not info.context.user.has_perms(MobilePaymentConfig.gql_query_transactions_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
            
        show_hsitory = kwargs.get('show_history', False)
        if not show_hsitory:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get('client_mutation_id', None)
        if client_mutation_id:
            filters.append( Q(mutations__mutation__client_mutation_id=client_mutation_id) )

        return gql_optimizer.query(Transactions.objects.filter(*filters).all(), info)


class Mutation(graphene.ObjectType):

    initiate_Transaction = InitiateTransactionMutation.Field()
    process_Transaction =  ProcessTransactionMutation.Field()
    process_payment = ProcessPayment.Field()



def on_transaction_mutation(kwargs, k= "uuid"):
    """
    This method is called on signal binding for scheme mutation
    """

    #get uuid from data
    transaction_uuid = kwargs['data'].get('uuid', None)

    if not transaction_uuid:
        return []
    impacted_transaction = Transactions.objects.get(Q(uuid=transaction_uuid))
    TransactionMutation.objects.create(transaction=impacted_transaction, mutation_id=kwargs['mutation_log_id'])
    return []

def on_transactions_mutation(**kwargs):
    uuids = kwargs['data'].get('uuids', [])

    if not uuids:
        uuid = kwargs['data'].get('uuid', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted_transacions = Transactions.objects.filter(uuid__in=uuids).all()
    for transaction in impacted_transacions:
        TransactionMutation.objects.create(transaction=transaction, mutation_id =kwargs['mutation_log_id'])
    return []

def bind_signals():
    signal_mutation_module_validate["mobile_payment"].connect(on_transactions_mutation)
    


    