from django.apps import AppConfig

MODULE_NAME = "mobile_payment"

DEFAULT_CFG = {
      
      "default_validations_disabled":False,
      "gql_query_payment_transaction_perms":["111001"],
      "gql_query_payment_service_provider":   ["101305"],
      "gql_mutation_create_payment_transaction_perms":["1110002"],
      "gql_mutation_update_payment_transaction_perms":["1110004"],
      "gql_mutation_verify_insuree_perms":["1110003"],
      "gql_mutation_process_payment_perms":["1110001"],
      "gql_mutation_create_payment_service_provider":["101306"],
      "gql_mutation_update_payment_service_provider":["101307"],
      "gql_mutation_delete_payment_service_provider":["101308"],
        
}

class MobilepaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_payment'
    gql_query_payment_transaction_perms = []
    gql_mutation_create_payment_transaction_perms =[]
    gql_query_payment_service_provider =   []
    gql_mutation_update_payment_transaction_perms = []
    gql_mutation_verify_insuree_perms = []
    gql_mutation_process_payment_perms = []
    gql_mutation_create_payment_service_provider =   []
    gql_mutation_update_payment_service_provider =   []
    gql_mutation_delete_payment_service_provider =   []

    def _configure_perms(self, cfg):
          MobilepaymentConfig.gql_query_payment_transaction_perms = cfg["gql_query_payment_transaction_perms"]
          MobilepaymentConfig.gql_query_payment_service_provider  = cfg["gql_query_payment_service_provider"]
          MobilepaymentConfig.gql_mutation_create_payment_transaction_perms = cfg["gql_mutation_create_payment_transaction_perms"]
          MobilepaymentConfig.gql_mutation_update_payment_transaction_perms = cfg["gql_mutation_update_payment_transaction_perms"]
          MobilepaymentConfig.gql_mutation_verify_insuree_perms = cfg["gql_mutation_verify_insuree_perms"]
          MobilepaymentConfig.gql_mutation_process_payment_perms = cfg["gql_mutation_process_payment_perms"]
          MobilepaymentConfig.gql_mutation_create_payment_service_provider =   cfg["gql_mutation_create_payment_service_provider"]
          MobilepaymentConfig.gql_mutation_update_payment_service_provider =   cfg["gql_mutation_update_payment_service_provider"]
          MobilepaymentConfig.gql_mutation_delete_payment_service_provider =   cfg["gql_mutation_delete_payment_service_provider"]

    def ready(self):
            from core.models import ModuleConfiguration
            cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
            self._configure_perms(cfg)


