from django.utils import timezone


def year(request):
    tz_year = timezone.now().year
    return {
        'year': tz_year
    }
