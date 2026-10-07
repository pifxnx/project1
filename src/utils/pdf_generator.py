import io
from pathlib import Path
import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot
from fpdf import FPDF

FONT = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"


def _row(values) -> list[str]:
    return ["" if v is None else str(v) for v in values]


def _chart(products):
    times = sorted(p["aggregated_at"] for p in products if p["aggregated_at"])
    if not times:
        return None

    fig, ax = pyplot.subplots(figsize=(9, 4))
    ax.step(times, range(1, len(times) + 1), where="post")
    ax.set_title("Агрегация по времени")
    ax.set_xlabel("Время")
    ax.set_ylabel("Агрегировано, шт.")
    fig.autofmt_xdate()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    pyplot.close(fig)
    buf.seek(0)
    return buf


def generate_batch_report_pdf(batch, products, stats, file_path):
    pdf = FPDF()
    pdf.add_font("DejaVu", fname=str(FONT))
    pdf.set_font("DejaVu", size=11)

    pdf.add_page()
    with pdf.table(first_row_as_headings=False) as table:
        table.row(_row(batch.keys()))
        table.row(_row(batch.values()))

    pdf.add_page()
    with pdf.table(first_row_as_headings=False) as table:
        table.row(["ID", "Уникальный код", "Агрегирован", "Дата агрегации"])
        for p in products:
            table.row(
                _row(
                    [
                        p["id"],
                        p["unique_code"],
                        "да" if p["is_aggregated"] else "нет",
                        p["aggregated_at"],
                    ]
                )
            )

    pdf.add_page()
    with pdf.table(first_row_as_headings=False) as table:
        table.row(_row(stats.keys()))
        table.row(_row(stats.values()))

    chart = _chart(products)
    pdf.ln(8)
    if chart:
        pdf.image(chart, w=pdf.epw)
    else:
        pdf.cell(text="Нет данных для графика")

    pdf.output(file_path)
