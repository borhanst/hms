import csv
import importlib
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.utils import timezone
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from scrapy.http import HtmlResponse, Request

from pharmacy.importers import merge_medicine_dataset
from pharmacy.models import Medicine
from core.models import User
from doctors.models import Doctor
from patients.models import Patient
from prescriptions.models import Prescription, PrescriptionItem
from scraper.medex.items import BrandItem, GenericItem
from scraper.medex.spiders.brands_spider import MedexBrandsSpider


class ScrapMedicenCommandTests(TestCase):
    def test_scrapy_pipeline_imports_project_models(self):
        import scraper.medex.pipelines as pipelines

        pipelines = importlib.reload(pipelines)

        self.assertEqual(pipelines.GenericMedicine._meta.label, "pharmacy.GenericMedicine")
        self.assertEqual(pipelines.BrandMedicine._meta.label, "pharmacy.BrandMedicine")

    def test_scrapy_project_uses_reactor_compatible_with_crochet(self):
        from scraper.medex import settings as medex_settings

        self.assertEqual(
            medex_settings.TWISTED_REACTOR,
            "twisted.internet.epollreactor.EPollReactor",
        )

    def test_listing_page_extracts_generic_links_and_next_page(self):
        spider = MedexBrandsSpider()
        response = HtmlResponse(
            url="https://dev.medex.com.bd/generics?alpha=a",
            request=Request("https://dev.medex.com.bd/generics?alpha=a"),
            body="""
                <html><body>
                    <a href="https://dev.medex.com.bd/generics/3/aceclofenac" class="hoverable-block darker">
                        <div class="row data-row">
                            <div class="col-xs-12 data-row-top dcind-title">Aceclofenac</div>
                            <div class="col-xs-12 dcind">137 available brands</div>
                        </div>
                    </a>
                    <a href="https://dev.medex.com.bd/generics/4/acetazolamide" class="hoverable-block darker">
                        <div class="row data-row">
                            <div class="col-xs-12 data-row-top dcind-title">Acetazolamide</div>
                            <div class="col-xs-12 dcind">2 available brands</div>
                        </div>
                    </a>
                    <a href="https://dev.medex.com.bd/generics?alpha=a&page=2">2</a>
                </body></html>
            """,
            encoding="utf-8",
        )

        results = list(spider.parse(response))
        detail_requests = [result for result in results if isinstance(result, Request)]

        self.assertEqual(
            [request.url for request in detail_requests[:2]],
            [
                "https://dev.medex.com.bd/generics/3/aceclofenac",
                "https://dev.medex.com.bd/generics/4/acetazolamide",
            ],
        )
        self.assertTrue(detail_requests[2].url.endswith("/generics?alpha=a&page=2"))

    def test_generic_detail_extracts_brand_names_url_and_generic_item(self):
        spider = MedexBrandsSpider()
        response = HtmlResponse(
            url="https://dev.medex.com.bd/generics/3/aceclofenac",
            request=Request("https://dev.medex.com.bd/generics/3/aceclofenac"),
            body="""
                <html><body>
                    <h1>Aceclofenac</h1>
                    <a href="https://dev.medex.com.bd/generics/3/aceclofenac/brand-names">Available brands</a>
                </body></html>
            """,
            encoding="utf-8",
        )

        results = list(spider.parse_generic_detail(response))
        generic_items = [result for result in results if isinstance(result, GenericItem)]
        brand_requests = [result for result in results if isinstance(result, Request)]

        self.assertEqual(len(generic_items), 1)
        self.assertEqual(generic_items[0]["name"], "Aceclofenac")
        self.assertEqual(generic_items[0]["url"], "https://dev.medex.com.bd/generics/3/aceclofenac")
        self.assertEqual(generic_items[0]["brand_names_url"], "https://dev.medex.com.bd/generics/3/aceclofenac/brand-names")
        self.assertEqual([request.url for request in brand_requests], ["https://dev.medex.com.bd/generics/3/aceclofenac/brand-names"])

    def test_brand_page_extracts_brand_rows_from_current_layout(self):
        spider = MedexBrandsSpider()
        response = HtmlResponse(
            url="https://dev.medex.com.bd/generics/3/aceclofenac/brand-names",
            request=Request("https://dev.medex.com.bd/generics/3/aceclofenac/brand-names"),
            body="""
                <html><body>
                    <h1>Aceclofenac</h1>
                    <table class="bindex-table">
                        <tbody id="gwb-body">
                            <tr class="brand-row" data-name="A-Pak" data-strength="100 mg" data-dosage-form="1" data-href="https://dev.medex.com.bd/brands/38193/a-pak-100-mg-tablet">
                                <td data-col="name">A-Pak</td>
                                <td>Tablet</td>
                                <td>100 mg</td>
                                <td>Benham Pharmaceuticals Ltd.</td>
                                <td data-col="price"><div class="package-container"><span>Unit Price:</span><span>৳ 5.00</span><span class="pack-size-info">(10 x 10: ৳ 500.00)</span></div></td>
                            </tr>
                            <tr class="brand-row" data-name="A-Pak SR" data-strength="200 mg" data-dosage-form="37" data-href="https://dev.medex.com.bd/brands/35356/a-pak-sr-200-mg-tablet">
                                <td data-col="name">A-Pak SR</td>
                                <td>Tablet (Sustained Release)</td>
                                <td>200 mg</td>
                                <td>Benham Pharmaceuticals Ltd.</td>
                                <td data-col="price"><div class="package-container"><span>Unit Price:</span><span>৳ 8.00</span><span class="pack-size-info">(5 x 10: ৳ 400.00)</span></div></td>
                            </tr>
                        </tbody>
                    </table>
                    <a href="https://dev.medex.com.bd/generics/3/aceclofenac/brand-names?page=2">Next</a>
                </body></html>
            """,
            encoding="utf-8",
        )

        results = list(spider.parse_brand_names(response))
        brand_items = [result for result in results if isinstance(result, BrandItem)]
        brand_requests = [result for result in results if isinstance(result, Request)]

        self.assertEqual(len(brand_items), 2)
        self.assertEqual(brand_items[0]["generic_name"], "Aceclofenac")
        self.assertEqual(brand_items[0]["generic_url"], "https://dev.medex.com.bd/generics/3/aceclofenac")
        self.assertEqual(brand_items[0]["brand_name"], "A-Pak")
        self.assertEqual(brand_items[0]["dosage_form"], "Tablet")
        self.assertEqual(brand_items[0]["strength"], "100 mg")
        self.assertEqual(brand_items[0]["company"], "Benham Pharmaceuticals Ltd.")
        self.assertIn("Unit Price: ৳ 5.00", brand_items[0]["pack_size_price"])
        self.assertEqual(brand_items[0]["brand_detail_url"], "https://dev.medex.com.bd/brands/38193/a-pak-100-mg-tablet")
        self.assertEqual([request.url for request in brand_requests], ["https://dev.medex.com.bd/generics/3/aceclofenac/brand-names?page=2"])

    def test_scraper_command_waits_for_crawl_and_restores_working_directory(self):
        from pharmacy.management.commands import scrap_medicen

        original_cwd = os.getcwd()
        stdout = StringIO()

        with patch.object(scrap_medicen, "run_medex_brands_scraper", return_value="finished") as run_scraper:
            call_command("scrap_medicen", stdout=stdout)

        run_scraper.assert_called_once_with()
        self.assertEqual(os.getcwd(), original_cwd)
        self.assertIn("Medex scraping completed.", stdout.getvalue())

    def test_scraper_command_raises_command_error_on_crawl_failure(self):
        from pharmacy.management.commands import scrap_medicen

        original_cwd = os.getcwd()

        with patch.object(scrap_medicen, "run_medex_brands_scraper", side_effect=RuntimeError("boom")):
            with self.assertRaisesMessage(CommandError, "Medex scraping failed: boom"):
                call_command("scrap_medicen", stdout=StringIO())

        self.assertEqual(os.getcwd(), original_cwd)

    def test_run_medex_brands_scraper_restores_cwd_after_blocking_crawl(self):
        from pharmacy.management.commands import scrap_medicen

        original_cwd = os.getcwd()

        with (
            patch.object(scrap_medicen, "get_project_settings", return_value={"setting": "value"}) as get_settings,
            patch.object(scrap_medicen, "CrawlerRunner") as runner_class,
            patch.object(scrap_medicen, "_crawl_medex_brands", return_value="finished") as crawl,
        ):
            result = scrap_medicen.run_medex_brands_scraper()

        get_settings.assert_called_once_with()
        runner_class.assert_called_once_with({"setting": "value"})
        crawl.assert_called_once_with(runner_class.return_value)
        self.assertEqual(result, "finished")
        self.assertEqual(os.getcwd(), original_cwd)


class ImportMedicinesCommandTests(TestCase):
    def write_csv(self, rows, headers):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "medicine.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def run_import(self, csv_path, **options):
        stdout = StringIO()
        call_command("import_medicines", str(csv_path), stdout=stdout, **options)
        return stdout.getvalue()

    def test_imports_and_infers_core_fields(self):
        csv_path = self.write_csv(
            [
                {
                    "brand name": "Napa Extra",
                    "medicine type": "Allopathic",
                    "dosage form": "Tablet",
                    "generic": "Paracetamol",
                    "strength": "500 mg",
                    "manufacturer": "Beximco Pharmaceuticals Ltd.",
                    "package container": "10's strip",
                    "package size": "25.50 BDT",
                },
                {
                    "brand name": "Herbal Care Syrup",
                    "medicine type": "Herbal",
                    "dosage form": "Syrup",
                    "generic": "",
                    "strength": "200 ml",
                    "manufacturer": "Herbal Co.",
                    "package container": "Bottle",
                    "package size": "",
                },
                {
                    "brand name": "Unknown Product",
                    "medicine type": "",
                    "dosage form": "",
                    "generic": "",
                    "strength": "",
                    "manufacturer": "",
                    "package container": "",
                    "package size": "invalid",
                },
            ],
            ["brand name", "medicine type", "dosage form", "generic", "strength", "manufacturer", "package container", "package size"],
        )

        output = self.run_import(
            csv_path,
            update_existing=True,
            default_stock=0,
            reorder_level=10,
        )

        self.assertIn("created=3", output)
        napa = Medicine.objects.get(name="Napa Extra")
        self.assertEqual(napa.generic_name, "Paracetamol")
        self.assertEqual(napa.category, "TABLET")
        self.assertEqual(napa.manufacturer, "Beximco Pharmaceuticals Ltd.")
        self.assertEqual(napa.unit_price, Decimal("25.50"))
        self.assertEqual(napa.stock, 0)
        self.assertEqual(napa.reorder_level, 10)
        self.assertIn("500 mg", napa.description)
        self.assertIn("10's strip", napa.description)

        herbal = Medicine.objects.get(name="Herbal Care Syrup")
        self.assertEqual(herbal.category, "SYRUP")
        self.assertEqual(herbal.unit_price, Decimal("0.00"))

        unknown = Medicine.objects.get(name="Unknown Product")
        self.assertEqual(unknown.category, "OTHER")
        self.assertEqual(unknown.unit_price, Decimal("0.00"))

    def test_updates_existing_medicine_when_requested(self):
        Medicine.objects.create(
            name="Napa Extra",
            generic_name="Old Generic",
            category="CAPSULE",
            manufacturer="Old Manufacturer",
            stock=17,
            unit_price=Decimal("5.00"),
            reorder_level=3,
            description="Existing note",
        )

        csv_path = self.write_csv(
            [
                {
                    "brand name": "Napa Extra",
                    "medicine type": "Allopathic",
                    "dosage form": "Tablet",
                    "generic": "Paracetamol",
                    "strength": "500 mg",
                    "manufacturer": "Beximco Pharmaceuticals Ltd.",
                    "package container": "Blister pack",
                    "package size": "Blister pack",
                    "price": "30.00",
                }
            ],
            ["brand name", "medicine type", "dosage form", "generic", "strength", "manufacturer", "package container", "package size", "price"],
        )

        output = self.run_import(
            csv_path,
            update_existing=True,
            default_stock=0,
            reorder_level=10,
        )

        self.assertIn("updated=1", output)
        napa = Medicine.objects.get(name="Napa Extra")
        self.assertEqual(napa.generic_name, "Paracetamol")
        self.assertEqual(napa.category, "TABLET")
        self.assertEqual(napa.manufacturer, "Beximco Pharmaceuticals Ltd.")
        self.assertEqual(napa.unit_price, Decimal("30.00"))
        self.assertEqual(napa.stock, 17)
        self.assertEqual(napa.reorder_level, 10)
        self.assertIn("Existing note", napa.description)
        self.assertIn("500 mg", napa.description)


class MergeMedicineDatasetTests(TestCase):
    def write_csv(self, folder, filename, headers, rows):
        path = Path(folder) / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_merges_reference_files_into_single_output_csv(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        source_dir = Path(temp_dir.name) / "medicein-dataset"
        source_dir.mkdir()
        output_path = Path(temp_dir.name) / "merged_medicines.csv"

        self.write_csv(
            source_dir,
            "medicine.csv",
            ["brand id", "brand name", "type", "slug", "dosage form", "generic", "strength", "manufacturer", "package container", "Package Size"],
            [
                {
                    "brand id": "4077",
                    "brand name": "A-Cold",
                    "type": "allopathic",
                    "slug": "a-coldsyrup4-mg5-ml",
                    "dosage form": "Syrup",
                    "generic": "Bromhexine Hydrochloride",
                    "strength": "4 mg/5 ml",
                    "manufacturer": "ACME Laboratories Ltd.",
                    "package container": "100 ml bottle",
                    "Package Size": "100 ml bottle: 40.12",
                },
                {
                    "brand id": "4078",
                    "brand name": "A-Cold",
                    "type": "allopathic",
                    "slug": "a-coldsyrup8-mg5-ml",
                    "dosage form": "Syrup",
                    "generic": "Bromhexine Hydrochloride",
                    "strength": "8 mg/5 ml",
                    "manufacturer": "ACME Laboratories Ltd.",
                    "package container": "200 ml bottle",
                    "Package Size": "200 ml bottle: 70.00",
                },
                {
                    "brand id": "9001",
                    "brand name": "B-Cap",
                    "type": "allopathic",
                    "slug": "b-capcapsule500-mg",
                    "dosage form": "Capsule",
                    "generic": "Paracetamol",
                    "strength": "500 mg",
                    "manufacturer": "Beximco Pharmaceuticals Ltd.",
                    "package container": "strip",
                    "Package Size": "strip: 5.00",
                },
            ],
        )

        self.write_csv(
            source_dir,
            "generic.csv",
            ["generic id", "generic name", "slug", "monograph link", "drug class", "indication", "indication description", "therapeutic class description", "pharmacology description", "dosage description", "administration description", "interaction description", "contraindications description", "side effects description", "pregnancy and lactation description", "precautions description", "pediatric usage description", "overdose effects description", "duration of treatment description", "reconstitution description", "storage conditions description", "descriptions count"],
            [
                {
                    "generic id": "145",
                    "generic name": "Bromhexine Hydrochloride",
                    "slug": "bromhexine-hydrochloride-145",
                    "monograph link": "",
                    "drug class": "Cough expectorants & mucolytics",
                    "indication": "Bronchitis",
                    "indication description": "Helpful for productive cough.",
                    "therapeutic class description": "Cough expectorants & mucolytics",
                    "pharmacology description": "Mucolytic agent.",
                    "dosage description": "Adult dose.",
                    "administration description": "",
                    "interaction description": "",
                    "contraindications description": "",
                    "side effects description": "",
                    "pregnancy and lactation description": "",
                    "precautions description": "",
                    "pediatric usage description": "",
                    "overdose effects description": "",
                    "duration of treatment description": "",
                    "reconstitution description": "",
                    "storage conditions description": "",
                    "descriptions count": "3",
                },
                {
                    "generic id": "200",
                    "generic name": "Paracetamol",
                    "slug": "paracetamol-200",
                    "monograph link": "",
                    "drug class": "Analgesics",
                    "indication": "Fever",
                    "indication description": "Reduces fever.",
                    "therapeutic class description": "Analgesics",
                    "pharmacology description": "Pain relief.",
                    "dosage description": "Adult dose.",
                    "administration description": "",
                    "interaction description": "",
                    "contraindications description": "",
                    "side effects description": "",
                    "pregnancy and lactation description": "",
                    "precautions description": "",
                    "pediatric usage description": "",
                    "overdose effects description": "",
                    "duration of treatment description": "",
                    "reconstitution description": "",
                    "storage conditions description": "",
                    "descriptions count": "3",
                },
            ],
        )

        self.write_csv(
            source_dir,
            "dosage form.csv",
            ["dosage form id", "dosage form name", "slug", "brand names count"],
            [
                {"dosage form id": "1", "dosage form name": "Syrup", "slug": "syrup-1", "brand names count": "1"},
                {"dosage form id": "2", "dosage form name": "Capsule", "slug": "capsule-2", "brand names count": "1"},
            ],
        )

        self.write_csv(
            source_dir,
            "manufacturer.csv",
            ["manufacturer id", "manufacturer name", "slug", "generics count", "brand names count"],
            [
                {"manufacturer id": "3", "manufacturer name": "ACME Laboratories Ltd.", "slug": "acme-3", "generics count": "1", "brand names count": "2"},
                {"manufacturer id": "4", "manufacturer name": "Beximco Pharmaceuticals Ltd.", "slug": "beximco-4", "generics count": "1", "brand names count": "1"},
            ],
        )

        self.write_csv(
            source_dir,
            "drug class.csv",
            ["drug class id", "drug class name", "slug", "generics count"],
            [
                {"drug class id": "21", "drug class name": "Cough expectorants & mucolytics", "slug": "cough-expectorants-21", "generics count": "1"},
                {"drug class id": "22", "drug class name": "Analgesics", "slug": "analgesics-22", "generics count": "1"},
            ],
        )

        self.write_csv(
            source_dir,
            "indication.csv",
            ["indication id", "indication name", "slug", "generics count"],
            [
                {"indication id": "2011", "indication name": "Bronchitis", "slug": "bronchitis-2011", "generics count": "1"},
                {"indication id": "2008", "indication name": "Fever", "slug": "fever-2008", "generics count": "1"},
            ],
        )

        summary = merge_medicine_dataset(source_dir, output_path)

        self.assertEqual(summary["source_rows"], 3)
        self.assertEqual(summary["merged_rows"], 2)

        with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 2)
        a_cold = next(row for row in rows if row["brand name"] == "A-Cold")
        self.assertEqual(a_cold["generic"], "Bromhexine Hydrochloride")
        self.assertEqual(a_cold["manufacturer"], "ACME Laboratories Ltd.")
        self.assertEqual(a_cold["dosage form"], "Syrup")
        self.assertEqual(a_cold["package size"], "100 ml bottle")
        self.assertEqual(a_cold["price"], "40.12")
        self.assertNotIn("40.12", a_cold["package size"])
        self.assertIn("Cough expectorants & mucolytics", a_cold["description"])
        self.assertIn("Bronchitis", a_cold["description"])
        self.assertIn("variant", a_cold["description"].lower())

        b_cap = next(row for row in rows if row["brand name"] == "B-Cap")
        self.assertEqual(b_cap["price"], "5.00")
        self.assertEqual(b_cap["package size"], "strip")


class PharmacyOperationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="pharmacist",
            password="password123",
            role=User.Role.PHARMACIST,
        )
        self.patient = Patient.objects.create(
            first_name="Ayesha",
            last_name="Rahman",
            gender="F",
            date_of_birth="1990-01-01",
            age=34,
            phone="01700000000",
            address="Dhaka",
        )
        self.medicine = Medicine.objects.create(
            name="Napa",
            generic_name="Paracetamol",
            category="TABLET",
            manufacturer="Beximco",
            stock=5,
            unit_price=Decimal("12.50"),
            reorder_level=10,
        )
        self.doctor_user = User.objects.create_user(
            username="doctor",
            password="password123",
            role=User.Role.DOCTOR,
            first_name="Ibrahim",
            last_name="Khan",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Medicine",
            department="GENERAL",
            consultation_fee=Decimal("500.00"),
        )

    def test_medicine_expiry_helpers_identify_expired_and_near_expiry(self):
        expired = Medicine.objects.create(
            name="Expired Syrup",
            category="SYRUP",
            stock=4,
            unit_price=Decimal("80.00"),
            expiry_date=timezone.localdate() - timezone.timedelta(days=1),
        )
        near_expiry = Medicine.objects.create(
            name="Near Expiry Tablet",
            category="TABLET",
            stock=8,
            unit_price=Decimal("5.00"),
            expiry_date=timezone.localdate() + timezone.timedelta(days=30),
        )
        valid = Medicine.objects.create(
            name="Valid Tablet",
            category="TABLET",
            stock=8,
            unit_price=Decimal("5.00"),
            expiry_date=timezone.localdate() + timezone.timedelta(days=31),
        )

        self.assertTrue(expired.is_expired)
        self.assertFalse(expired.is_near_expiry)
        self.assertEqual(expired.days_until_expiry, -1)
        self.assertTrue(near_expiry.is_near_expiry)
        self.assertFalse(valid.is_near_expiry)
        self.assertFalse(self.medicine.is_expired)
        self.assertFalse(self.medicine.is_near_expiry)
        self.assertIsNone(self.medicine.days_until_expiry)

    def test_completing_purchase_increases_stock_and_records_movement(self):
        from pharmacy.models import Purchase, PurchaseItem, StockMovement, Supplier

        supplier = Supplier.objects.create(name="Beximco Supplier", phone="01711111111")
        purchase = Purchase.objects.create(supplier=supplier, reference_number="PO-001", status="DRAFT")
        PurchaseItem.objects.create(
            purchase=purchase,
            medicine=self.medicine,
            quantity=20,
            unit_cost=Decimal("9.25"),
        )

        purchase.complete(received_by=self.user)

        self.medicine.refresh_from_db()
        purchase.refresh_from_db()
        self.assertEqual(self.medicine.stock, 25)
        self.assertEqual(purchase.status, "COMPLETED")
        self.assertEqual(purchase.total, Decimal("185.00"))
        movement = StockMovement.objects.get(medicine=self.medicine, movement_type="PURCHASE")
        self.assertEqual(movement.quantity, 20)
        self.assertEqual(movement.unit_price, Decimal("9.25"))

    def test_sale_decreases_stock_and_creates_invoice_items(self):
        from billing.models import Invoice, InvoiceItem
        from pharmacy.models import PharmacySale, PharmacySaleItem, StockMovement

        sale = PharmacySale.objects.create(patient=self.patient, sold_by=self.user)
        PharmacySaleItem.objects.create(
            sale=sale,
            medicine=self.medicine,
            quantity=3,
            unit_price=self.medicine.unit_price,
        )

        invoice = sale.complete()

        self.medicine.refresh_from_db()
        sale.refresh_from_db()
        self.assertEqual(self.medicine.stock, 2)
        self.assertEqual(sale.status, "COMPLETED")
        self.assertEqual(sale.total, Decimal("37.50"))
        self.assertEqual(invoice, sale.invoice)
        self.assertEqual(Invoice.objects.count(), 1)
        item = InvoiceItem.objects.get(invoice=invoice)
        self.assertEqual(item.description, "Napa")
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(invoice.total, Decimal("37.50"))
        self.assertEqual(StockMovement.objects.filter(medicine=self.medicine, movement_type="SALE").count(), 1)

    def test_sale_blocks_insufficient_stock(self):
        from pharmacy.models import PharmacySale, PharmacySaleItem

        sale = PharmacySale.objects.create(patient=self.patient, sold_by=self.user)
        PharmacySaleItem.objects.create(
            sale=sale,
            medicine=self.medicine,
            quantity=6,
            unit_price=self.medicine.unit_price,
        )

        with self.assertRaisesMessage(ValueError, "Insufficient stock"):
            sale.complete()

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 5)

    def test_sale_blocks_expired_medicine(self):
        from pharmacy.models import PharmacySale, PharmacySaleItem

        self.medicine.expiry_date = timezone.localdate() - timezone.timedelta(days=1)
        self.medicine.save(update_fields=["expiry_date"])
        sale = PharmacySale.objects.create(patient=self.patient, sold_by=self.user)
        PharmacySaleItem.objects.create(
            sale=sale,
            medicine=self.medicine,
            quantity=1,
            unit_price=self.medicine.unit_price,
        )

        with self.assertRaisesMessage(ValueError, "expired"):
            sale.complete()

        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 5)

    def test_sale_create_prefills_from_prescription(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Fever",
        )
        PrescriptionItem.objects.create(
            prescription=prescription,
            medicine=self.medicine,
            medicine_name=self.medicine.name,
            dosage="500 mg",
            quantity=3,
            unit_price=self.medicine.unit_price,
            frequency="BD",
            duration="5 days",
        )
        client = Client()
        client.force_login(self.user)

        response = client.get(reverse("pharmacy:sale_create"), {"from_prescription": prescription.pk})

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        formset = response.context["formset"]
        self.assertEqual(form.initial["patient"], self.patient)
        self.assertEqual(form.initial["prescription"], prescription)
        self.assertEqual(formset.forms[0].initial["medicine"], self.medicine)
        self.assertEqual(formset.forms[0].initial["quantity"], 3)
        self.assertEqual(formset.forms[0].initial["unit_price"], self.medicine.unit_price)
        self.assertContains(response, f'value="{self.patient.pk}" selected')
        self.assertContains(response, f'value="{self.medicine.pk}" selected')

    def test_sale_create_from_prescription_requires_pharmacy_permission(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Fever",
        )
        client = Client()
        client.force_login(self.doctor_user)

        response = client.get(reverse("pharmacy:sale_create"), {"from_prescription": prescription.pk})

        self.assertRedirects(response, reverse("core:dashboard"))

    def test_prescription_detail_shows_invoice_sale_button_for_pharmacist(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Fever",
        )
        client = Client()
        client.force_login(self.user)

        response = client.get(reverse("prescriptions:prescription_detail", args=[prescription.pk]))

        self.assertContains(response, "Create Invoice")
        self.assertContains(response, f"{reverse('pharmacy:sale_create')}?from_prescription={prescription.pk}")

    def test_prescription_detail_hides_invoice_sale_button_without_pharmacy_permission(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Fever",
        )
        client = Client()
        client.force_login(self.doctor_user)

        response = client.get(reverse("prescriptions:prescription_detail", args=[prescription.pk]))

        self.assertNotContains(response, "Create Invoice")

    def test_dispensing_blocks_expired_medicine(self):
        self.medicine.expiry_date = timezone.localdate() - timezone.timedelta(days=1)
        self.medicine.save(update_fields=["expiry_date"])
        client = Client()
        client.force_login(self.user)

        response = client.post(reverse("pharmacy:dispensing_create"), {
            "medicine": self.medicine.pk,
            "quantity": 1,
            "dispensed_by": "Pharmacist",
            "notes": "",
        })

        self.assertEqual(response.status_code, 200)
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 5)
        self.assertContains(response, "expired")

    def test_medicine_list_filters_expired_and_near_expiry(self):
        expired = Medicine.objects.create(
            name="Expired Syrup",
            category="SYRUP",
            stock=4,
            unit_price=Decimal("80.00"),
            expiry_date=timezone.localdate() - timezone.timedelta(days=1),
        )
        near_expiry = Medicine.objects.create(
            name="Near Expiry Tablet",
            category="TABLET",
            stock=8,
            unit_price=Decimal("5.00"),
            expiry_date=timezone.localdate() + timezone.timedelta(days=30),
        )
        Medicine.objects.create(
            name="Valid Tablet",
            category="TABLET",
            stock=8,
            unit_price=Decimal("5.00"),
            expiry_date=timezone.localdate() + timezone.timedelta(days=31),
        )
        client = Client()
        client.force_login(self.user)

        expired_response = client.get(reverse("pharmacy:medicine_list"), {"expiry_status": "expired"})
        near_response = client.get(reverse("pharmacy:medicine_list"), {"expiry_status": "near_expiry"})

        self.assertContains(expired_response, expired.name)
        self.assertNotContains(expired_response, near_expiry.name)
        self.assertContains(near_response, near_expiry.name)
        self.assertNotContains(near_response, expired.name)

    def test_dispose_expired_medicine_sets_stock_to_zero_and_records_adjustment(self):
        from pharmacy.models import StockMovement

        self.medicine.expiry_date = timezone.localdate() - timezone.timedelta(days=1)
        self.medicine.save(update_fields=["expiry_date"])
        client = Client()
        client.force_login(self.user)

        response = client.post(reverse("pharmacy:medicine_dispose_expired", args=[self.medicine.pk]))

        self.assertRedirects(response, reverse("pharmacy:medicine_list"))
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 0)
        movement = StockMovement.objects.get(medicine=self.medicine, movement_type="ADJUSTMENT")
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.performed_by, self.user)
        self.assertIn("Expired stock disposed", movement.notes)

    def test_pharmacist_can_open_full_pharmacy_pages(self):
        from pharmacy.models import Supplier

        supplier = Supplier.objects.create(name="Beximco Supplier")
        client = Client()
        client.force_login(self.user)

        urls = [
            reverse("pharmacy:pharmacy_dashboard"),
            reverse("pharmacy:supplier_list"),
            reverse("pharmacy:supplier_create"),
            reverse("pharmacy:supplier_edit", args=[supplier.pk]),
            reverse("pharmacy:purchase_list"),
            reverse("pharmacy:purchase_create"),
            reverse("pharmacy:sale_list"),
            reverse("pharmacy:sale_create"),
            reverse("pharmacy:stock_movement_list"),
            reverse("pharmacy:pharmacy_reports"),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, 200)

    def test_sale_and_purchase_forms_render_full_width_formset_container(self):
        client = Client()
        client.force_login(self.user)

        for url_name in ("pharmacy:sale_create", "pharmacy:purchase_create"):
            with self.subTest(url_name=url_name):
                response = client.get(reverse(url_name))

                self.assertContains(response, 'id="formset-container"')
                self.assertContains(response, "formset-row")
                self.assertNotContains(response, ">Id</label>")
                self.assertNotContains(response, ">Sale</label>")
                self.assertNotContains(response, ">Purchase</label>")
