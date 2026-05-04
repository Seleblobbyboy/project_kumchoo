from django.utils import timezone
from stadium.models import Match

class MatchStatusAutoUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            current_datetime = timezone.localtime()
            current_date = current_datetime.date()
            current_time = current_datetime.time()

            # 1. Scheduled -> Live
            Match.objects.filter(
                status='scheduled',
                match_date=current_date,
                start_time__lte=current_time,
                end_time__gt=current_time
            ).update(status='live')

            # 2. Scheduled/Live -> Completed (Past Date)
            Match.objects.filter(
                status__in=['scheduled', 'live'],
                match_date__lt=current_date
            ).update(status='completed')

            # 3. Scheduled/Live -> Completed (Today, after end time)
            Match.objects.filter(
                status__in=['scheduled', 'live'],
                match_date=current_date,
                end_time__lte=current_time
            ).update(status='completed')
        except Exception:
            pass

        response = self.get_response(request)
        return response
