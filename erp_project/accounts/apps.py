from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Use full dotted path so Django resolves the app correctly when the
    # project lives inside the ``erp_project`` package.
    name = "erp_project.accounts"
