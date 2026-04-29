from django.core.management.base import BaseCommand, CommandError

from pharmacy.importers import import_medicines_from_csv


class Command(BaseCommand):
    help = "Import medicine catalog data from a CSV file into the pharmacy app."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Path to the medicine CSV file.")
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update rows that already exist instead of skipping them.",
        )
        parser.add_argument(
            "--default-stock",
            type=int,
            default=0,
            help="Stock level assigned to newly created medicines.",
        )
        parser.add_argument(
            "--reorder-level",
            type=int,
            default=10,
            help="Reorder threshold assigned to imported medicines.",
        )
        parser.add_argument(
            "--reset-stock",
            action="store_true",
            help="Reset existing medicines to the default stock when updating them.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        try:
            summary = import_medicines_from_csv(
                csv_path,
                update_existing=options["update_existing"],
                default_stock=options["default_stock"],
                reorder_level=options["reorder_level"],
                reset_stock=options["reset_stock"],
            )
        except FileNotFoundError as exc:
            raise CommandError(f"CSV file not found: {csv_path}") from exc

        self.stdout.write(
            "Import complete: "
            f"rows={summary['rows_seen']} "
            f"created={summary['created']} "
            f"updated={summary['updated']} "
            f"skipped={summary['skipped']} "
            f"warnings={summary['warnings']}"
        )
