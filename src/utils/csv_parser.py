import csv
from .excel_generator import EXPORT_HEADERS


headers = [
    "batch_number",
    "batch_date",
    "is_closed",
    "task_description",
    "work_center_identifier",
    "shift",
    "team",
    "nomenclature",
    "ekn_code",
    "total_products",
    "aggregated_products",
    "shift_start",
    "shift_end",
]
header_lang_map = dict(zip(EXPORT_HEADERS, headers))


class CSVParserException(Exception):
    pass


def replace_values(row):
    new_row = []
    for v in row:
        if v == "Открыта":
            new_row.append(False)
        elif v == "Закрыта":
            new_row.append(True)
        else:
            new_row.append(v)
    return new_row


def parse_batches_csv(filename):
    with open(filename, encoding="utf-8-sig", newline="") as f:
        sample = f.read(1024)
        if not sample.strip():
            raise CSVParserException("файл пустой")
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        except csv.Error:
            raise CSVParserException("не удалось определить разделитель")
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)

        if not reader.fieldnames:
            raise CSVParserException("файл пустой")
        unknown = [h for h in reader.fieldnames if h not in header_lang_map]
        if unknown:
            raise CSVParserException(f"неизвестные заголовки {unknown}")
        headers = [header_lang_map[h] for h in reader.fieldnames]

        for row in reader:
            yield dict(zip(headers, replace_values(row.values())))
