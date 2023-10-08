from django.core.management.base import BaseCommand
from authentication.models import CourseraToken

class Command(BaseCommand):
    help = 'Create default tokens'

    def handle(self, *args, **kwargs):
        defaults = [
            {'item': 'initial_code', 'value': 'default_initial_code'},
            {'item': 'access_token', 'value': 'default_access_token'},
            {'item': 'refresh_token', 'value': 'default_refresh_token'},
        ]

        for data in defaults:
            CourseraToken.objects.get_or_create(**data)

        self.stdout.write(self.style.SUCCESS('Default tokens created.'))
