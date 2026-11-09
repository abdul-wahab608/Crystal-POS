from django.core.management.base import BaseCommand

from products.models import Color, SizeRange

SIZE_RANGES = ['Kids (24-30)', 'Women (36-41)', 'Men (40-46)']
COLORS = ['Black', 'Brown', 'Tan', 'White', 'Navy', 'Maroon', 'Grey', 'Beige']


class Command(BaseCommand):
    help = 'Create the default size ranges and colors (idempotent).'

    def handle(self, *args, **options):
        for name in SIZE_RANGES:
            SizeRange.objects.get_or_create(name=name)
        for name in COLORS:
            Color.objects.get_or_create(name=name)
        self.stdout.write(f'Size ranges: {SizeRange.objects.count()}, colors: {Color.objects.count()}')
