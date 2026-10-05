from fpdf import FPDF

LABELS = {
    "Номер партии": "Batch number",
    "Дата партии": "Batch date",
    "Статус": "Closed",
    "Рабочий центр": "Work center",
    "Смена": "Shift",
    "Бригада": "Team",
    "Номенклатура": "Nomenclature",
    "Начало смены": "Shift start",
    "Окончание смены": "Shift end",
    "Всего продукции": "Total products",
    "Аггрегировано": "Aggregated",
    "Осталось": "Remaining",
    "Процент выполнения": "Completion, %",
}


def _row(values) -> list[str]:
    return [
        ("" if v is None else str(v)).encode("latin-1", "replace").decode("latin-1")
        for v in values
    ]


def _labels(keys) -> list[str]:
    return _row(LABELS.get(k, k) for k in keys)


def generate_batch_report_pdf(
    batch: dict, products: list[dict], stats: dict, file_path: str
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    with pdf.table(first_row_as_headings=False) as table:
        table.row(_labels(batch.keys()))
        table.row(_row(batch.values()))

    pdf.add_page()
    with pdf.table(first_row_as_headings=False) as table:
        table.row(["ID", "Unique code", "Aggregated", "Aggregation date"])
        for p in products:
            table.row(
                _row(
                    [
                        p["id"],
                        p["unique_code"],
                        "yes" if p["is_aggregated"] else "no",
                        p["aggregated_at"],
                    ]
                )
            )

    pdf.add_page()
    with pdf.table(first_row_as_headings=False) as table:
        table.row(_labels(stats.keys()))
        table.row(_row(stats.values()))

    pdf.output(file_path)
