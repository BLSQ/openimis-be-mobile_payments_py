from django.db import models
import uuid
from django.utils import timezone
from core import models as core_models
from insuree.models import Insuree
from django.conf import settings
from graphql import ResolveInfo
from django.utils.translation import gettext_lazy as _

        
class  PaymentServiceProvider(core_models.VersionedModel):
    id = models.AutoField(db_column="PspID", primary_key=True)
    uuid = models.CharField(db_column="PspUUID", max_length=36, default=uuid.uuid4, unique=True)
    name = models.CharField(db_column= "PspName", max_length=50, unique=True)
    account = models.CharField( db_column= "PspAccount", max_length= 36,blank=True, null=True)
    pin = models.CharField(db_column=" PspPin", max_length=128, blank=True, null=True)
    email = models.EmailField(db_column="PspEmail", max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(db_column="DateCreated", blank=True, default=timezone.now)
    is_external_api_user = models.BooleanField(default=False)
    interactive_user = models.ForeignKey("core.InteractiveUser", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_queryset(cls,queryset, user):
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        return queryset
    
    class Meta:
        managed = True
        db_table = "tblPaymentServiceProviders"
        
class ApiUtilitie(models.Model):
    id  = models.AutoField(db_column="ApiId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=50, blank= True, null=True)
    access_token = models.TextField(db_column="AccessToken", blank=True, null=True)
    access_TokenExpiry = models.DateTimeField(db_column="ExpiryDate", blank= True, null= True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        db_table = 'tblApiUtilitie'


class PaymentTransaction(core_models.VersionedModel):
    id  = models.AutoField(db_column="PaymentTransactionId", primary_key=True )
    uuid = models.CharField(
        db_column="TransactionUUID", max_length=36, default=uuid.uuid4, unique=True)
    amount = models.DecimalField(db_column="Amount", max_digits=18, decimal_places=2)
    payment_service_provider = models.ForeignKey(PaymentServiceProvider, models.DO_NOTHING, db_column= "PSPUUID",
                                       blank= True,
                                       null=True,
                                       related_name= "payment_transactions")
    insuree = models.ForeignKey(Insuree, models.DO_NOTHING, db_column= "InsureeUUID",
                                       blank= True,
                                       null=True,
                                       related_name= "payment_transactions")
    psp_transaction_id =  models.CharField(db_column="PspTransactionID", blank=True, max_length=125)
    otp = models.CharField(db_column="OTP", blank=True, null=True, max_length= 10)
    status = models.BooleanField(db_column="PaymentTransactionStatus", blank=True, default= False)
    json_content = models.TextField(db_column="JsonContent", blank=True, null=True)
    datetime = models.DateTimeField(db_column="Datetime", blank=True, default=timezone.now)

    class Meta():

        managed = True
        db_table = 'tblPaymentTransaction' 

class ApiRecord(models.Model):
    id  = models.AutoField(db_column="ApiRecordID", primary_key=True )
    uuid = models.CharField(
        db_column="ApiRecordUUID", max_length=36, default=uuid.uuid4, unique=True)
    request_date = models.TextField(db_column="RequestedData", blank=True, null=True)
    response_date = models.TextField(db_column="ResponseData", blank=True, null=True)
    time_stamp = models.DateTimeField(db_column="TimeStamp", auto_now_add=timezone.now)


    class Meta:
        managed = True
        db_table = "tblApiRecord"

class PaymentTransactionMutation(core_models.UUIDModel, core_models.ObjectMutation):
    transaction  = models.ForeignKey(PaymentTransaction, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payment_transactions')

    class Meta:
        managed = True
        db_table = "mobilePayment_PaymentTransactionMutation"

class PaymentServiceProviderMutation(core_models.UUIDModel, core_models.ObjectMutation):
    payment_service_provider  = models.ForeignKey(PaymentServiceProvider, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payment_service_providers')

    class Meta:
        managed = True
        db_table = "mobilePayment_PaymentServiceProviderMutation"


