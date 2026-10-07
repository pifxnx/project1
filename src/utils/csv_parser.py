import csv
from .excel_parser import header_lang_map


class CSVParserException(Exception):
    pass


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
            yield dict(zip(headers, row.values()))
