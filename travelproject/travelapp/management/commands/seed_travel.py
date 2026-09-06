from django.core.management.base import BaseCommand
from travelapp.views import seed_data
class Command(BaseCommand):
    help = 'Create default travel categories and packages'
    def handle(self, *args, **kwargs):
        seed_data()
        self.stdout.write(self.style.SUCCESS('Default packages created successfully'))
