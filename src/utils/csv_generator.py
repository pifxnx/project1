import csv
from .excel_generator import EXPORT_HEADERS, export_row


def generate_export_batches_csv(batches: list[dict], file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(EXPORT_HEADERS)
        for b in batches:
            writer.writerow(export_row(b))
