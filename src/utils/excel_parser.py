from openpyxl import load_workbook


class ExcelParserException(Exception):
    pass


header_lang_map = {
    "ПредставлениеЗаданияНаСмену": "task_description",
    "РабочийЦентр": "work_center_name",
    "ИдентификаторРЦ": "work_center_identifier",
    "СтатусЗакрытия": "is_closed",
    "Смена": "shift",
    "Бригада": "team",
    "НомерПартии": "batch_number",
    "ДатаПартии": "batch_date",
    "Номенклатура": "nomenclature",
    "КодЕКН": "ekn_code",
    "ДатаВремяНачалаСмены": "shift_start",
    "ДатаВремяОкончанияСмены": "shift_end",
}


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


def parse_batches_excel(filename):
    wb = load_workbook(filename=filename, read_only=True)
    try:
        sheet = wb.active
        rows = sheet.iter_rows(values_only=True)
        try:
            headers = next(rows)
        except StopIteration:
            raise ExcelParserException("файл пустой")

        unknown = [h for h in headers if h not in header_lang_map]
        if unknown:
            raise ExcelParserException(f"неизвестные заголовки {unknown}")
        headers = [header_lang_map[h] for h in headers]

        for row in rows:
            yield dict(zip(headers, replace_values(row)))

    finally:
        wb.close()
