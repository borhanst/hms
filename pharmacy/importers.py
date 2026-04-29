import csv
import html
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Medicine


HEADER_ALIASES = {
    "name": ("brandname", "medicinename", "name", "brand"),
    "generic_name": ("generic", "genericname"),
    "manufacturer": ("manufacturer", "company", "pharmaceuticalcompany"),
    "category": ("dosageform", "form", "category", "type", "medicinetype"),
    "strength": ("strength",),
    "package_container": ("packagecontainer", "packageinfo", "packinfo", "package"),
    "package_size": ("packagesize", "unitprice", "price", "mrp", "retailprice"),
    "description": ("description", "indication", "use", "uses"),
}

CATEGORY_PATTERNS = [
    ("TABLET", [r"\btablet\b", r"\btab\b", r"\bcaplet\b", r"\bchewable\b"]),
    ("CAPSULE", [r"\bcapsule\b", r"\bcap\b"]),
    ("SYRUP", [r"\bsyrup\b", r"\bsuspension\b", r"\belixir\b"]),
    ("INJECTION", [r"\binjection\b", r"\biv\b", r"\bim\b", r"\binj\b"]),
    ("CREAM", [r"\bcream\b", r"\bointment\b", r"\bgel\b", r"\btopical\b"]),
    ("DROPS", [r"\bdrops\b", r"\bdrop\b"]),
    ("INHALER", [r"\binhaler\b"]),
    ("SUPPOSITORY", [r"\bsuppository\b"]),
]


def normalize_header(value):
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def build_header_map(fieldnames):
    lookup = {}
    for field in fieldnames or []:
        lookup[normalize_header(field)] = field
    return lookup


def first_value(row, header_map, aliases):
    for alias in aliases:
        key = header_map.get(alias)
        if key:
            value = row.get(key, "")
            if value is not None:
                value = str(value).strip()
                if value:
                    return value
    return ""


def collect_values(row, header_map, aliases):
    values = []
    for alias in aliases:
        key = header_map.get(alias)
        if key:
            value = row.get(key, "")
            if value is not None:
                value = str(value).strip()
                if value and value not in values:
                    values.append(value)
    return values


def unique_non_empty(values):
    seen = set()
    result = []
    for value in values:
        value = str(value).strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def infer_category(*texts):
    haystack = " ".join(filter(None, texts)).lower()
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, haystack):
                return category
    return "OTHER"


def parse_price(value, *, allow_plain_integer=False):
    text = str(value or "").strip()
    if not text:
        return None

    unit_price_match = re.search(
        r"unit\s*price\s*:?\s*(?:bdt|tk|taka|rs|\u09f3)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
        text,
        flags=re.I,
    )
    if unit_price_match:
        try:
            return Decimal(unit_price_match.group(1).replace(",", ""))
        except InvalidOperation:
            return None

    normalized = text.replace(" ", "")
    if not allow_plain_integer and "." not in normalized and not re.search(r"\b(bdt|tk|taka|rs|price|mrp)\b", text.lower()):
        return None

    matches = re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", normalized)
    if not matches:
        return None

    candidate = matches[-1].replace(",", "")
    try:
        return Decimal(candidate)
    except InvalidOperation:
        return None


def extract_unit_price(row, header_map):
    for alias_group in (
        (("unitprice", "price", "mrp", "retailprice"), True),
        (("packagesize",), False),
        (("packagecontainer", "packageinfo", "packinfo", "package"), False),
    ):
        aliases, allow_plain_integer = alias_group
        for alias in aliases:
            key = header_map.get(alias)
            if not key:
                continue
            value = parse_price(row.get(key), allow_plain_integer=allow_plain_integer)
            if value is not None:
                return value
    return Decimal("0.00")


def build_description(row, header_map):
    parts = []
    for alias_group in (
        ("strength",),
        ("packagecontainer", "packageinfo", "packinfo", "package"),
        ("packagesize",),
        ("description", "indication", "use", "uses"),
    ):
        parts.extend(collect_values(row, header_map, alias_group))
    return "\n".join(unique_non_empty(parts))


def normalize_name(value):
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def normalize_row_keys(row):
    return {normalize_header(key): (value or "").strip() for key, value in row.items()}


def get_row_value(row, *candidate_keys):
    for candidate in candidate_keys:
        key = normalize_header(candidate)
        value = row.get(key, "")
        if value:
            return str(value).strip()
    return ""


def load_normalized_csv_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [normalize_row_keys(row) for row in csv.DictReader(handle)]


def join_unique(values, separator=" | "):
    return separator.join(unique_non_empty(values))


def strip_html(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def format_price(value):
    price = parse_price(value, allow_plain_integer=False)
    if price is None:
        return ""
    return f"{price.quantize(Decimal('0.01'))}"


def clean_package_text(value):
    text = str(value or "").strip()
    if not text:
        return ""

    text = re.sub(
        r"unit\s*price\s*:?\s*(?:bdt|tk|taka|rs|\u09f3)?\s*\d+(?:,\d{3})*(?:\.\d+)?",
        " ",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"(?:bdt|tk|taka|rs|\u09f3)\s*\d+(?:,\d{3})*(?:\.\d+)?",
        " ",
        text,
        flags=re.I,
    )
    text = re.sub(r":\s*\d+(?:,\d{3})*(?:\.\d+)?", " ", text)
    text = re.sub(r"\(\s*,?\s*\)", " ", text)
    text = re.sub(r"[(),]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" :-")


def pick_parseable_price_text(row):
    for field in ("package size", "package container", "price", "mrp", "retail price"):
        value = get_row_value(row, field)
        if value and parse_price(value, allow_plain_integer=False) is not None:
            return value
    return get_row_value(row, "package size", "package container", "price", "mrp", "retail price")


def select_canonical_medicine_row(rows):
    def row_score(row, index):
        score = 0
        if pick_parseable_price_text(row):
            score += 5
        if get_row_value(row, "dosage form"):
            score += 2
        if get_row_value(row, "generic"):
            score += 2
        if get_row_value(row, "manufacturer"):
            score += 1
        return score, -index

    best_index, best_row = max(enumerate(rows), key=lambda item: row_score(item[1], item[0]))
    return best_row


def build_generic_reference_index(source_dir):
    generic_rows = load_normalized_csv_rows(Path(source_dir) / "generic.csv")
    return {
        normalize_name(get_row_value(row, "generic name")): row
        for row in generic_rows
        if get_row_value(row, "generic name")
    }


def build_dataset_summary(row_group, generic_index):
    canonical = select_canonical_medicine_row(row_group)
    unique_brand_ids = [get_row_value(row, "brand id") for row in row_group]
    unique_types = [get_row_value(row, "type") for row in row_group]
    unique_slugs = [get_row_value(row, "slug") for row in row_group]
    unique_dosage_forms = [get_row_value(row, "dosage form") for row in row_group]
    unique_generics = [get_row_value(row, "generic") for row in row_group]
    unique_strengths = [get_row_value(row, "strength") for row in row_group]
    unique_manufacturers = [get_row_value(row, "manufacturer") for row in row_group]
    unique_containers = [
        clean_package_text(get_row_value(row, "package container"))
        for row in row_group
    ]
    unique_package_sizes = [
        clean_package_text(get_row_value(row, "package size", "package container"))
        for row in row_group
    ]
    unique_prices = [format_price(pick_parseable_price_text(row)) for row in row_group]
    canonical_package_size = clean_package_text(
        get_row_value(canonical, "package size", "package container")
    )
    canonical_container = clean_package_text(get_row_value(canonical, "package container"))
    canonical_price = format_price(pick_parseable_price_text(canonical))

    generic_classes = []
    generic_indications = []
    generic_snippets = []

    for generic_name in unique_non_empty(unique_generics):
        generic_row = generic_index.get(normalize_name(generic_name))
        if not generic_row:
            continue
        generic_classes.append(get_row_value(generic_row, "drug class"))
        generic_indications.append(get_row_value(generic_row, "indication"))
        for field in (
            "indication description",
            "therapeutic class description",
            "pharmacology description",
            "dosage description",
            "contraindications description",
            "side effects description",
            "precautions description",
            "storage conditions description",
        ):
            snippet = strip_html(get_row_value(generic_row, field))
            if snippet:
                generic_snippets.append(snippet)
                break

    description_parts = []
    description_parts.append(
        "Variants: "
        f"{len(row_group)} row(s); "
        f"dosage forms={join_unique(unique_dosage_forms) or 'n/a'}; "
        f"strengths={join_unique(unique_strengths) or 'n/a'}; "
        f"manufacturers={join_unique(unique_manufacturers) or 'n/a'}; "
        f"containers={join_unique(unique_containers) or 'n/a'}; "
        f"prices={join_unique(unique_prices) or 'n/a'}"
    )
    if generic_classes:
        description_parts.append(f"Drug class: {join_unique(generic_classes)}")
    if generic_indications:
        description_parts.append(f"Indication: {join_unique(generic_indications)}")
    if generic_snippets:
        description_parts.append(f"Reference: {join_unique(generic_snippets, separator=' / ')}")

    return {
        "brand id": get_row_value(canonical, "brand id"),
        "brand name": get_row_value(canonical, "brand name"),
        "type": join_unique(unique_types),
        "slug": get_row_value(canonical, "slug"),
        "dosage form": join_unique(unique_dosage_forms) or get_row_value(canonical, "dosage form"),
        "generic": join_unique(unique_generics) or get_row_value(canonical, "generic"),
        "strength": join_unique(unique_strengths) or get_row_value(canonical, "strength"),
        "manufacturer": join_unique(unique_manufacturers) or get_row_value(canonical, "manufacturer"),
        "package container": canonical_container or join_unique(unique_containers),
        "package size": canonical_package_size or join_unique(unique_package_sizes),
        "price": canonical_price,
        "drug class": join_unique(generic_classes),
        "indication": join_unique(generic_indications),
        "description": "\n".join(unique_non_empty(description_parts)),
        "variant count": str(len(row_group)),
    }


def merge_medicine_dataset(source_dir, output_path):
    source_dir = Path(source_dir)
    output_path = Path(output_path)

    medicine_rows = load_normalized_csv_rows(source_dir / "medicine.csv")
    generic_index = build_generic_reference_index(source_dir)

    grouped_rows = {}
    group_order = []
    for row in medicine_rows:
        brand_name = get_row_value(row, "brand name")
        if not brand_name:
            continue
        key = normalize_name(brand_name)
        if key not in grouped_rows:
            grouped_rows[key] = []
            group_order.append(key)
        grouped_rows[key].append(row)

    merged_rows = [
        build_dataset_summary(grouped_rows[key], generic_index)
        for key in group_order
    ]

    fieldnames = [
        "brand id",
        "brand name",
        "type",
        "slug",
        "dosage form",
        "generic",
        "strength",
        "manufacturer",
        "package container",
        "package size",
        "price",
        "drug class",
        "indication",
        "description",
        "variant count",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

    return {
        "source_rows": len(medicine_rows),
        "merged_rows": len(merged_rows),
        "output_path": str(output_path),
    }


def import_medicines_from_csv(
    csv_path,
    *,
    update_existing=False,
    default_stock=0,
    reorder_level=10,
    reset_stock=False,
):
    path = Path(csv_path)
    created = 0
    updated = 0
    skipped = 0
    warnings = 0
    rows_seen = 0

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header_map = build_header_map(reader.fieldnames)

        for raw_row in reader:
            rows_seen += 1
            row = {key: (value or "").strip() for key, value in raw_row.items()}

            name = first_value(row, header_map, HEADER_ALIASES["name"])
            if not name:
                skipped += 1
                warnings += 1
                continue

            generic_name = first_value(row, header_map, HEADER_ALIASES["generic_name"])
            manufacturer = first_value(row, header_map, HEADER_ALIASES["manufacturer"])
            category = infer_category(
                " ".join(collect_values(row, header_map, HEADER_ALIASES["category"])),
                first_value(row, header_map, HEADER_ALIASES["strength"]),
                first_value(row, header_map, HEADER_ALIASES["package_container"]),
                first_value(row, header_map, HEADER_ALIASES["package_size"]),
                name,
                generic_name,
            )
            unit_price = extract_unit_price(row, header_map)
            description = build_description(row, header_map)

            medicine, created_flag = Medicine.objects.get_or_create(
                name=name,
                defaults={
                    "generic_name": generic_name,
                    "category": category,
                    "manufacturer": manufacturer,
                    "stock": default_stock,
                    "unit_price": unit_price,
                    "reorder_level": reorder_level,
                    "description": description,
                },
            )

            if created_flag:
                created += 1
                continue

            if not update_existing:
                skipped += 1
                continue

            if reset_stock:
                medicine.stock = default_stock

            medicine.generic_name = generic_name
            medicine.category = category
            medicine.manufacturer = manufacturer
            medicine.unit_price = unit_price
            medicine.reorder_level = reorder_level

            if description:
                if medicine.description:
                    if description not in medicine.description:
                        medicine.description = "\n".join(
                            unique_non_empty([medicine.description, description])
                        )
                else:
                    medicine.description = description

            medicine.save()
            updated += 1

    return {
        "rows_seen": rows_seen,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "warnings": warnings,
    }
