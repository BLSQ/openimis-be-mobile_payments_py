import graphene
from graphene_django import DjangoObjectType
from mobile_payment.models import Transactions
from insuree.gql_queries import InsureeGQLType
from contribution.gql_queries import PaymentServiceProviderGQLType
from core import prefix_filterset, ExtendedConnection, filter_validity

class TransactionsGQLType(DjangoObjectType):

    """ Transaction Query fields"""
    client_mutation_id = graphene.String()

    class Meta:

        model = Transactions
        interfaces = (graphene.relay.Node,)
        filter_fields = {

            "id": ["exact"],
            "uuid": ["exact"],
            "amount":[ "exact", "lt", "gt"],
            "transaction_id": ["exact"], 
            "otp":["exact"],
            "status": ["exact"],
            "datetime": ["exact"],
            **prefix_filterset("PaymentServiceProvider__", PaymentServiceProviderGQLType._meta.filter_fields),
            **prefix_filterset("Insuree__", InsureeGQLType._meta.filter_fields),
        }
        
        connection_class = ExtendedConnection
        
# *********************************** Afri Money ***********************************

class PolicyType(graphene.ObjectType):
    product_name = graphene.String()
    amount = graphene.Float()
    status = graphene.Int()

class VerifyGQLtype(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    policies = graphene.List(PolicyType)
    message = graphene.String()

class CustomMessagetype(graphene.ObjectType):
    message = graphene.String()     
