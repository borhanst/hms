# scraper/medex/pipelines.py

import os
import sys
from pathlib import Path

import django


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms.settings")
django.setup()

from pharmacy.models import GenericMedicine, BrandMedicine
from .items import GenericItem, BrandItem


class MedexPipeline:
    def process_item(self, item, spider=None):
        if isinstance(item, GenericItem):
            GenericMedicine.objects.update_or_create(
                url=item["url"],
                defaults={
                    "name": item["name"],
                    "brand_names_url": item["brand_names_url"],
                },
            )
            return item

        if isinstance(item, BrandItem):
            generic, _ = GenericMedicine.objects.update_or_create(
                url=item["generic_url"],
                defaults={
                    "name": item["generic_name"],
                    "brand_names_url": item["brand_names_url"],
                },
            )

            BrandMedicine.objects.update_or_create(
                brand_detail_url=item["brand_detail_url"],
                defaults={
                    "generic": generic,
                    "brand_name": item["brand_name"],
                    "dosage_form": item["dosage_form"],
                    "strength": item["strength"],
                    "company": item["company"],
                    "pack_size_price": item["pack_size_price"],
                    "source_url": item["source_url"],
                },
            )
            return item

        return item
