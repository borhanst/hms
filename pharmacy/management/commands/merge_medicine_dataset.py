from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from pharmacy.importers import merge_medicine_dataset


class Command(BaseCommand):
    help = "Merge the Kaggle medicine dataset folder into a single CSV for database import."

    def add_arguments(self, parser):
        parser.add_argument(
            "source_dir",
            nargs="?",
            default="medicein-dataset",
            help="Directory containing medicine.csv and the reference CSV files.",
        )
        parser.add_argument(
            "--output",
            default=None,
            help="Destination CSV file. Defaults to <source_dir>/merged_medicines.csv.",
        )

    def handle(self, *args, **options):
        source_dir = Path(options["source_dir"])
        output_path = Path(options["output"]) if options["output"] else source_dir / "merged_medicines.csv"

        if not source_dir.exists():
            raise CommandError(f"Source directory not found: {source_dir}")

        summary = merge_medicine_dataset(source_dir, output_path)
        self.stdout.write(
            "Merge complete: "
            f"source_rows={summary['source_rows']} "
            f"merged_rows={summary['merged_rows']} "
            f"output={summary['output_path']}"
        )
