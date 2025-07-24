import csv
from django.core.management.base import BaseCommand, CommandParser
from piecemeal_app.models import FoodItem


class Command(BaseCommand):
    help = "Remove and reload FoodItems from a CSV file."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        basename = csv_path.split("/")[-1]

        # remove old items
        deleted, _ = FoodItem.objects.filter(common_csv_filename=basename).delete()
        self.stdout.write(
            self.style.WARNING(f"Deleted {deleted} FoodItems from old {basename}")
        )

        # create the new food items
        created = 0
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                FoodItem.objects.create(
                    is_meal=False,
                    owner=None,
                    is_public=True,
                    quantity=100.0,
                    unit="g",
                    name=row.get("name"),
                    aisle=row.get("aisle"),
                    calories=float((row.get("calories") or "0.0").strip()),
                    protein=float((row.get("protein") or "0.0").strip()),
                    carbs=float((row.get("carbs") or "0.0").strip()),
                    fats=float((row.get("fats") or "0.0").strip()),
                    common_csv_filename=basename,
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Added {created} new FoodItems from {basename}")
        )
