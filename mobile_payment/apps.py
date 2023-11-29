from django.apps import AppConfig

MODULE_NAME = "mobile_payment"

DEFAULT_CFG = {
      
      "default_validations_disabled":False,
      "gql_query_payment_transaction_perms":["208000"],
      "gql_mutation_create_payment_transaction_perms":["208001"],
      "gql_mutation_update_payment_transaction_perms":["208002"],
      "gql_query_verify_insuree_perms":["208003"],
      "gql_mutation_process_payment_perms":["208004"],
      "gql_query_payment_service_provider":["208005"],
      "gql_mutation_create_payment_service_provider_perms":["208006"],
      "gql_mutation_update_payment_service_provider_perms":["208007"],
      "gql_mutation_delete_payment_service_provider_perms":["208008"],
        
}

class MobilepaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_payment'
    gql_query_payment_transaction_perms = []
    gql_mutation_create_payment_transaction_perms =[]
    gql_query_payment_service_provider =   []
    gql_mutation_update_payment_transaction_perms = []
    gql_query_verify_insuree_perms = []
    gql_mutation_process_payment_perms = []
    gql_mutation_create_payment_service_provider_perms =   []
    gql_mutation_update_payment_service_provider_perms =   []
    gql_mutation_delete_payment_service_provider_perms =   []

    def _configure_perms(self, cfg):
          MobilepaymentConfig.gql_query_payment_transaction_perms = cfg["gql_query_payment_transaction_perms"]
          MobilepaymentConfig.gql_query_payment_service_provider  = cfg["gql_query_payment_service_provider"]
          MobilepaymentConfig.gql_mutation_create_payment_transaction_perms = cfg["gql_mutation_create_payment_transaction_perms"]
          MobilepaymentConfig.gql_mutation_update_payment_transaction_perms = cfg["gql_mutation_update_payment_transaction_perms"]
          MobilepaymentConfig.gql_query_verify_insuree_perms = cfg["gql_query_verify_insuree_perms"]
          MobilepaymentConfig.gql_mutation_process_payment_perms = cfg["gql_mutation_process_payment_perms"]
          MobilepaymentConfig.gql_mutation_create_payment_service_provider_perms =   cfg["gql_mutation_create_payment_service_provider_perms"]
          MobilepaymentConfig.gql_mutation_update_payment_service_provider_perms =   cfg["gql_mutation_update_payment_service_provider_perms"]
          MobilepaymentConfig.gql_mutation_delete_payment_service_provider_perms =   cfg["gql_mutation_delete_payment_service_provider_perms"]

    def ready(self):
            from core.models import ModuleConfiguration
            cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
            self._configure_perms(cfg)


