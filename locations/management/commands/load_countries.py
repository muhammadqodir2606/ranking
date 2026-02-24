import json

from django.core.management import BaseCommand

from locations.models import Country


class Command(BaseCommand):
    help = "Load countries from json"

    def handle(self, *args, **kwargs):
        with open("country.json", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            Country.objects.update_or_create(
                code=item["Code"],
                defaults={
                    "name": item["Name"],
                }
            )
        self.stdout.write(self.style.SUCCESS("Countries loaded"))

