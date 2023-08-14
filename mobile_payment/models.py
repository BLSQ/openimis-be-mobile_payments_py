from django.db import models
import uuid
from django.utils import timezone
from core import models as core_models
from insuree.models import Insuree
# Create your models here.

class Api_Utilities(models.Model):

    id  = models.AutoField(db_column="Api_Id", primary_key=True)
    name = models.CharField(db_column="Name", max_length=50, blank= True, null=True)
    access_token = models.TextField(db_column="access_token", blank=True, null=True)
    access_TokenExpiry = models.DateTimeField(db_column="ExpiryDate", blank= True, null= True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = True
        db_table = 'tblApi_Utilities'


class Transactions(core_models.VersionedModel):
    id  = models.AutoField(db_column="TransactionId", primary_key=True )
    uuid = models.CharField(
        db_column="TransactionUUID", max_length=36, default=uuid.uuid4, unique=True)
    amount = models.DecimalField(db_column="Amount", max_digits=18, decimal_places=2)
    PaymentServiceProvider = models.ForeignKey('contribution.PaymentServiceProvider', models.DO_NOTHING, db_column= "PSPUUID",
                                       blank= True,
                                       null=True,
                                       related_name= "transactions")
    Insuree = models.ForeignKey(Insuree, models.DO_NOTHING, db_column= "InsureeUUID",
                                       blank= True,
                                       null=True,
                                       related_name= "transactions")
    transaction_id =  models.CharField(db_column="transaction_id", blank=True, max_length=125)
    otp = models.CharField(db_column="OTP", blank=True, null=True, max_length= 10)
    status = models.BooleanField(db_column="transaction_status", blank=True, default= False)
    datetime = models.DateTimeField(db_column="Datetime", blank=True, default=timezone.now)

    class Meta():

        managed = True
        db_table = 'tblTransactions' 

class TransactionMutation(core_models.UUIDModel, core_models.ObjectMutation):
    transaction  = models.ForeignKey(Transactions, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='transactions')

    class Meta:
        managed = True
        db_table = "TransactionMutation"


