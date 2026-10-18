from django.conf import settings


def catalog_directions(request):
    """Предоставляет список направлений материалов во все шаблоны."""
    return {
        'CATALOG_DIRECTIONS': getattr(settings, 'DIRECTION_CHOICES', []),
    }
