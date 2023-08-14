from django.apps import AppConfig

MODULE_NAME = "mobile_payment"

DEFAULT_CFG = {
      
      "default_validations_disabled":False,
      "gql_query_transactions_perms":["111001"],
      "gql_mutation_create_transaction_perms":["1110002"],
      "gql_mutation_update_transaction_perms":["1110004"],
        
}

class MobilePaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_payment'
    gql_query_transactions_perms = []
    gql_mutation_create_transaction_perms =[]
    gql_mutation_update_transaction_perms = []

    def _configure_perms(self, cfg):
          MobilePaymentConfig.default_validations_disabled = cfg["default_validations_disabled"]
          MobilePaymentConfig.gql_query_transactions_perms = cfg["gql_query_transactions_perms"]
          MobilePaymentConfig.gql_mutation_create_transaction_perms = cfg["gql_mutation_create_transaction_perms"]
          MobilePaymentConfig.gql_mutation_update_transaction_perms = cfg["gql_mutation_update_transaction_perms"]

    def ready(self):
            from core.models import ModuleConfiguration
            cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
            self._configure_perms(cfg)


