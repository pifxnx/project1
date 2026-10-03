import csv
from .excel_parser import header_lang_map


class CSVParserException(Exception):
    pass


def parse_batches_csv(filename):
    with open(filename, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        unknown = [h for h in reader.fieldnames if h not in header_lang_map]
        if unknown:
            raise CSVParserException("неизвестные заголовки")
        headers = [header_lang_map[h] for h in reader.fieldnames]

        for row in reader:
            yield dict(zip(headers, row.values()))
