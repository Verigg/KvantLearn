from .models import SiteSettings


def site_settings(request):
    """Контекстный процессор для доступа к глобальным настройкам сайта из любого шаблона."""
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None
    return {
        'site_settings': settings_obj,
    }
