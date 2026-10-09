from src.utils.csv_parser import parse_batches_csv


def test_csv_parse_file(tmp_path):
    header = (
        "НомерПартии;ДатаПартии;СтатусЗакрытия;ПредставлениеЗаданияНаСмену;"
        "ИдентификаторРЦ;Смена;Бригада;Номенклатура;КодЕКН;"
        "ДатаВремяНачалаСмены;ДатаВремяОкончанияСмены"
    )

    row = (
        "{i};2023-01-01;Закрыта;ПредставлениеЗаданияНаСмену;"
        "ИдентификаторРЦ;Смена;Бригада;Номенклатура;КодЕКН;"
        "2023-01-01 08:00:00;2023-01-01 16:00:00"
    )

    path = tmp_path / "test.csv"

    path.write_text(
        header + "\n" + "\n".join([row.format(i=i) for i in range(1, 51)]),
        encoding="utf-8-sig",
    )

    rows = parse_batches_csv(path)

    assert len(list(rows)) == 50
