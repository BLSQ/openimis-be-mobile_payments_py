import graphene
from graphene_django import DjangoObjectType
from mobile_payment.models import Transactions, PaymentServiceProvider
from insuree.gql_queries import InsureeGQLType
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
            **prefix_filterset("insuree__", InsureeGQLType._meta.filter_fields),
        }
        
        connection_class = ExtendedConnection
        
# *********************************** Afri Money ***********************************

class PolicyType(graphene.ObjectType):
    product_name = graphene.String()
    amount = graphene.Float()
    status = graphene.Int()
    product_code = graphene.String()
    token = graphene.String()

class VerifyGQLtype(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    policies = graphene.List(PolicyType)
    message = graphene.String()

class CustomMessagetype(graphene.ObjectType):
    message = graphene.String()     


class ApiClientType(DjangoObjectType):
    class Meta:

        model = PaymentServiceProvider
        interfaces = (graphene.relay.Node,)
        filter_fields = {

            "id": ["exact"],
            "uuid": ["exact"],
            "psp_name":["exact"],
            "psp_username":["exact"],
            "psp_account": ["exact"],
            "email":["exact"],
        }
        exclude = ['psp_password', 'psp_pin']

        connection_class = ExtendedConnection