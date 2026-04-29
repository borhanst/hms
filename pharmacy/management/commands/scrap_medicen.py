# apps/medicines/management/commands/scrape_medex_brands.py

from django.core.management.base import BaseCommand, CommandError

import os
from pathlib import Path

from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


setup()


@wait_for(timeout=86400)
def _crawl_medex_brands(runner):
    return runner.crawl("medex_brands")


def run_medex_brands_scraper():
    base_dir = Path(__file__).resolve().parents[3]
    scraper_dir = base_dir / "scraper"
    current_dir = Path.cwd()

    try:
        os.chdir(scraper_dir)

        settings = get_project_settings()
        runner = CrawlerRunner(settings)

        return _crawl_medex_brands(runner)
    finally:
        os.chdir(current_dir)


class Command(BaseCommand):
    help = "Scrape Medex generic brand names data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting Medex scraper..."))

        try:
            run_medex_brands_scraper()
        except Exception as exc:
            raise CommandError(f"Medex scraping failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("Medex scraping completed."))
