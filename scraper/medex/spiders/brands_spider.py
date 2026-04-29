# scraper/medex/spiders/brands_spider.py
import os
import re

import scrapy

from ..items import BrandItem, GenericItem


BASE_URL = os.getenv("MEDEX_BASE_URL", "https://dev.medex.com.bd")


class MedexBrandsSpider(scrapy.Spider):
    name = "medex_brands"
    allowed_domains = ["medex.com.bd", "dev.medex.com.bd"]
    start_urls = [
        f"{BASE_URL}/generics",
        f"{BASE_URL}/generics?herbal=1",
    ]

    def parse(self, response):
        if "/brand-names" in response.url:
            yield from self.parse_brand_names(response)
            return

        for link in self.extract_generic_links(response):
            yield response.follow(link, callback=self.parse_generic_detail)

        next_page = self.get_next_page_url(response)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_generic_detail(self, response):
        generic_name = self.clean_text(response.css("h1::text").get())
        brand_names_url = response.css('a[href*="/brand-names"]::attr(href)').get()

        if not generic_name:
            return

        generic_url = response.url
        brand_names_url = response.urljoin(brand_names_url) if brand_names_url else ""

        yield GenericItem(
            name=generic_name,
            url=generic_url,
            brand_names_url=brand_names_url,
        )

        if brand_names_url:
            yield response.follow(
                brand_names_url,
                callback=self.parse_brand_names,
                meta={
                    "generic_name": generic_name,
                    "generic_url": generic_url,
                    "brand_names_url": brand_names_url,
                },
            )

    def parse_brand_names(self, response):
        generic_name = response.meta.get("generic_name") or self.clean_text(
            response.css("h1::text").get()
        )
        generic_url = response.meta.get("generic_url", response.url.rsplit("/brand-names", 1)[0])
        brand_names_url = response.meta.get("brand_names_url", response.url)

        yielded = False
        for item in self.extract_brand_items(response, generic_name, generic_url, brand_names_url):
            yielded = True
            yield item

        next_page = self.get_next_page_url(response)
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_brand_names,
                meta={
                    "generic_name": generic_name,
                    "generic_url": generic_url,
                    "brand_names_url": brand_names_url,
                },
            )

        if not yielded:
            self.logger.info("No brand items parsed for %s", response.url)

    def extract_generic_links(self, response):
        generic_links = []
        seen = set()
        for href in response.css("a::attr(href)").getall():
            match = re.search(r"/generics/\d+/[^/?#]+", href or "")
            if not match:
                continue
            url = response.urljoin(match.group(0))
            if url in seen:
                continue
            seen.add(url)
            generic_links.append(url)
        return generic_links

    def extract_brand_items(self, response, generic_name, generic_url, brand_names_url):
        rows = response.css("tr.brand-row")
        if rows:
            for row in rows:
                brand_name = self.clean_text(row.css('td[data-col="name"]::text').get() or row.attrib.get("data-name"))
                dosage_form = self.clean_text(" ".join(row.css("td:nth-child(2)::text").getall()) or row.attrib.get("data-dosage-form", ""))
                strength = self.clean_text(" ".join(row.css("td:nth-child(3)::text").getall()) or row.attrib.get("data-strength", ""))
                company = self.clean_text(" ".join(row.css("td:nth-child(4)::text").getall()))
                pack_size_price = self.clean_text(" ".join(row.css('td[data-col="price"] *::text, td[data-col="price"]::text').getall()))
                brand_detail_url = row.attrib.get("data-href", "")

                if not brand_name or not brand_detail_url:
                    continue

                yield BrandItem(
                    generic_name=generic_name,
                    generic_url=generic_url,
                    brand_names_url=brand_names_url,
                    brand_name=brand_name,
                    dosage_form=dosage_form,
                    strength=strength,
                    company=company,
                    pack_size_price=pack_size_price,
                    brand_detail_url=brand_detail_url,
                    source_url=response.url,
                )
            return

        brand_links = []
        seen = set()
        for href in response.css("a::attr(href)").getall():
            match = re.search(r"/brands/\d+/[^/?#]+", href or "")
            if not match:
                continue
            url = response.urljoin(match.group(0))
            if url in seen:
                continue
            seen.add(url)
            brand_links.append(url)

        for href in brand_links:
            link = response.css(f'a[href="{href}"]')
            brand_name = self.clean_text(" ".join(link.css("::text").getall()))
            container = link.xpath('ancestor::*[self::li or self::div][1]')
            tokens = [
                self.clean_text(text)
                for text in container.css("::text").getall()
                if self.clean_text(text)
            ]
            tokens = [token for token in tokens if not token.startswith("Image:")]

            price_index = next((index for index, token in enumerate(tokens) if token.startswith("Unit Price:")), None)
            if price_index is not None and price_index >= 4:
                dosage_form = tokens[1]
                strength = tokens[2]
                company = tokens[3]
                pack_size_price = tokens[price_index]
            else:
                dosage_form = tokens[1] if len(tokens) > 1 else ""
                strength = tokens[2] if len(tokens) > 2 else ""
                company = tokens[3] if len(tokens) > 3 else ""
                pack_size_price = " ".join(tokens[4:]) if len(tokens) > 4 else ""

            if not brand_name:
                continue

            yield BrandItem(
                generic_name=generic_name,
                generic_url=generic_url,
                brand_names_url=brand_names_url,
                brand_name=brand_name,
                dosage_form=dosage_form,
                strength=strength,
                company=company,
                pack_size_price=pack_size_price,
                brand_detail_url=href,
                source_url=response.url,
            )

    def get_next_page_url(self, response):
        current_page = self.extract_page_number(response.url)
        page_candidates = []

        for href in response.css("a[href*='page=']::attr(href)").getall():
            page_number = self.extract_page_number(href)
            if page_number is None:
                continue
            if current_page is None:
                page_candidates.append((page_number, href))
                continue
            if page_number > current_page:
                page_candidates.append((page_number, href))

        if not page_candidates:
            return ""

        page_candidates.sort(key=lambda item: item[0])
        return page_candidates[0][1]

    def extract_page_number(self, url):
        match = re.search(r"[?&]page=(\d+)", url or "")
        return int(match.group(1)) if match else None

    def clean_text(self, value):
        if not value:
            return ""

        return " ".join(value.split()).strip()
