import json

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient
from django.conf import settings


class Command(BaseCommand):
    help = 'Импорт ингридиентов из файла json'

    BASE_DIR = settings.BASE_DIR

    def handle(self, *args, **options):
        try:
            path = self.BASE_DIR / 'data/ingredients.json'
            with open(path) as file:
                data = json.load(file)
                for item in data:
                    Ingredient.objects.create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'])
        except CommandError as e:
            raise CommandError from e
