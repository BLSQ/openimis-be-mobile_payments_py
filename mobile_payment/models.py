from django.db import models
import uuid
from django.utils import timezone
from core import models as core_models
from insuree.models import Insuree
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from graphql import ResolveInfo
from django.utils.translation import gettext_lazy as _

        
class  PaymentServiceProvider(core_models.VersionedModel):
    id = models.AutoField(db_column="Psp_ID", primary_key=True)
    uuid = models.CharField(db_column="Psp_UUID", max_length=36, default=uuid.uuid4, unique=True)
    psp_name = models.CharField(db_column= "Psp_Name", max_length=50, unique=True)
    psp_username = models.CharField(db_column= "Psp_Username", max_length= 36, blank=True, null=True)
    psp_password = models.CharField(db_column= "Psp_Password", max_length=128, blank=True, null=True)
    psp_account = models.CharField( db_column= "Psp_Account", max_length= 36,blank=True, null=True)
    psp_pin = models.CharField(db_column=" Psp_Pin", max_length=128, blank=True, null=True)
    email = models.EmailField(db_column="Psp_email", max_length=100, blank=True, null=True)
    access_token = models.CharField(db_column="Api_client_access_token", max_length=128, blank=True, null=True)
    date_created = models.DateTimeField(db_column="Date_created", blank=True, default=timezone.now)
    has_login = models.BooleanField(db_column='HasLogin', blank=True, null=True)
    is_external_api_user = models.BooleanField(default=False)
    interactive_user = models.ForeignKey("core.InteractiveUser", on_delete=models.CASCADE, blank=True, null=True)
    json_content = models.TextField(db_column="Json_content", blank=True, null=True)

    def __str__(self):
        return self.psp_name
    
    USERNAME_FIELD = 'psp_username'

    
    @property
    def username(self):
        return self.psp_username

    def get_username(self):
        return self.psp_username
    
    def set_password(self, raw_password):
        self.psp_password = make_password(raw_password)
        print(self.psp_password)
        return self.psp_password

  
    def check_passwords(self, raw_password):
        print("Provided password:", raw_password)
        print("Stored password:", self.psp_password)
        
        password_match = check_password(raw_password, self.psp_password)
        print("Password match:", password_match)
        
        return password_match
    
    @classmethod
    def get_queryset(cls,queryset, user):
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        return queryset
    
    class Meta:
        managed = True
        db_table = "tblPaymnet_Service_Provider"

    



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
    payment_service_provider = models.ForeignKey(PaymentServiceProvider, models.DO_NOTHING, db_column= "PSPUUID",
                                       blank= True,
                                       null=True,
                                       related_name= "transactions")
    insuree = models.ForeignKey(Insuree, models.DO_NOTHING, db_column= "InsureeUUID",
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






class Api_Records(models.Model):
    id  = models.AutoField(db_column="Api_Record_ID", primary_key=True )
    uuid = models.CharField(
        db_column="Api_Record_UUID", max_length=36, default=uuid.uuid4, unique=True)
    # api_client = models.ForeignKey( Api_Client, models.DO_NOTHING, db_column="Api_clientID")
    request_date = models.TextField(db_column="requested_data", blank=True, null=True)
    response_date = models.TextField(db_column="response_data", blank=True, null=True)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now_add=timezone.now)


    class Meta:
        managed = True
        db_table = "Api_Records"

class TransactionMutation(core_models.UUIDModel, core_models.ObjectMutation):
    # transaction  = models.ForeignKey(Transactions, models.DO_NOTHING,
    #                           related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='transactions')

    class Meta:
        managed = True
        db_table = "TransactionMutation"

# class PaymentServiceProviderMutation(core_models.UUIDModel, core_models.ObjectMutation):
#     payment_service_provider  = models.ForeignKey(PaymentServiceProvider, models.DO_NOTHING,
#                               related_name='mutations')
#     mutation = models.ForeignKey(
#         core_models.MutationLog, models.DO_NOTHING, related_name='payment_service_provider')

#     class Meta:
#         managed = True
#         db_table = "PaymentServiceProviderMutation"


