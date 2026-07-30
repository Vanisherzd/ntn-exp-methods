#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PIL import Image
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

HERE: Final = Path(__file__).resolve().parent
REPO: Final = HERE.parents[1]
HW: Final = REPO / "hardware_conducted_iq"
RUN: Final = HW / "20260626_003643_gain20_50db"
OUT_PDF: Final = HERE / "fig_conducted_iq_evidence.pdf"

BLUE: Final = HexColor("#1F4E79")
RED: Final = HexColor("#9E2F28")
GRAY: Final = HexColor("#666666")
LINE: Final = HexColor("#B8B8B8")
PALE_BLUE: Final = HexColor("#EDF3F8")
PALE_RED: Final = HexColor("#F8ECEA")
PALE_GRAY: Final = HexColor("#F4F4F4")


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True, slots=True)
class RepeatStats:
    mean_db: float
    sd_db: float
    clipped: bool
    saturated: bool


@dataclass(frozen=True, slots=True)
class ControlStats:
    before_db: float
    after_db: float


@dataclass(frozen=True, slots=True)
class MatrixRow:
    label: str
    evidence: str
    boundary: str


def flag(raw: str) -> bool:
    return raw.strip().lower() == "true"


def repeat_stats() -> RepeatStats:
    with (HW / "repeatability_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    values = [float(row["txon_minus_noise_db"]) for row in rows]
    mean = sum(values) / len(values)
    sd = (sum((value - mean) ** 2 for value in values) / len(values)) ** 0.5
    return RepeatStats(
        mean_db=mean,
        sd_db=sd,
        clipped=any(flag(row["clipping_warning"]) for row in rows),
        saturated=any(flag(row["saturation_warning"]) for row in rows),
    )


def control_stats() -> ControlStats:
    with (HW / "before_after_reflash_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["phase"]: row for row in csv.DictReader(handle)}
    return ControlStats(
        before_db=float(rows["before_reflash"]["txon_minus_noise_db"]),
        after_db=float(rows["after_reflash"]["txon_minus_noise_db"]),
    )


def artifact_summary() -> dict[str, float | bool | str | list[str]]:
    with (RUN / "artifact_masked_signal_detection_summary.json").open(encoding="utf-8") as handle:
        data: dict[str, float | bool | str | list[str]] = json.load(handle)
    return data


def set_font(canvas: Canvas, size: float, bold: bool = False,
             color: Color = black) -> None:
    canvas.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    canvas.setFillColor(color)


def draw_text(canvas: Canvas, x: float, y: float, value: str, size: float = 6.2,
              bold: bool = False, color: Color = black) -> None:
    set_font(canvas, size, bold, color)
    canvas.drawString(x, y, value)


def center_text(canvas: Canvas, x: float, y: float, value: str, size: float = 6.2,
                bold: bool = False, color: Color = black) -> None:
    set_font(canvas, size, bold, color)
    canvas.drawCentredString(x, y, value)


def round_box(canvas: Canvas, rect: Rect, fill: Color, stroke: Color = LINE) -> None:
    canvas.setFillColor(fill)
    canvas.setStrokeColor(stroke)
    canvas.roundRect(rect.x, rect.y, rect.w, rect.h, 3.0, stroke=1, fill=1)


def arrow(canvas: Canvas, start_x: float, end_x: float, y: float) -> None:
    canvas.setStrokeColor(BLUE)
    canvas.setFillColor(BLUE)
    canvas.setLineWidth(0.9)
    canvas.line(start_x, y, end_x, y)
    path = canvas.beginPath()
    path.moveTo(end_x, y)
    path.lineTo(end_x - 4.5, y + 2.8)
    path.lineTo(end_x - 4.5, y - 2.8)
    path.close()
    canvas.drawPath(path, stroke=0, fill=1)


def draw_node(canvas: Canvas, rect: Rect, title: str, sub: str, fill: Color) -> None:
    round_box(canvas, rect, fill)
    center_text(canvas, rect.x + rect.w / 2, rect.y + rect.h - 8.0, title, 5.8, True)
    center_text(canvas, rect.x + rect.w / 2, rect.y + 8.0, sub, 4.55, False, GRAY)


def draw_protocol(canvas: Canvas, rect: Rect) -> None:
    draw_text(canvas, rect.x, rect.y + rect.h - 8, "A  Measurement protocol", 7.2, True)
    node_y = rect.y + 17
    node_h = 26
    widths = [42, 44, 37, 41, 45]
    titles = ["Det. FW", "LR1121", "50 dB", "USRP B210", "IQ analysis"]
    subs = ["923.2 MHz / -17 dBm", "NUCLEO-L476RG", "atten. coax", "RX2 A", "artifact-aware"]
    fills = [PALE_BLUE, white, white, PALE_GRAY, PALE_BLUE]
    x = rect.x + 2
    nodes: list[Rect] = []
    for width, title, sub, fill in zip(widths, titles, subs, fills):
        node = Rect(x, node_y, width, node_h)
        draw_node(canvas, node, title, sub, fill)
        nodes.append(node)
        x += width + 8
    for left, right in zip(nodes, nodes[1:]):
        arrow(canvas, left.x + left.w, right.x - 1.8, node_y + node_h / 2)
    tag_y = rect.y + 4
    for idx, tag in enumerate(["conducted", "RX-only", "no antenna", "no OTA path"]):
        draw_text(canvas, rect.x + 18 + idx * 50, tag_y, tag, 5.8, False, GRAY)


def matrix_rows(repeats: RepeatStats, controls: ControlStats,
                summary: dict[str, float | bool | str | list[str]]) -> list[MatrixRow]:
    peak_mhz = float(summary["peak_frequency_hz_after_mask"]) / 1e6
    return [
        MatrixRow("Serial verification", "TX_START -> repeated LR-FHSS bursts -> TX_DONE", "serial log"),
        MatrixRow("Before/after control", f"stock 868 MHz not visible (~{controls.before_db:.1f} dB); 923.2 MHz / -17 dBm visible", "same RX"),
        MatrixRow("Repeatability", f"{repeats.mean_db:.2f} +/- {repeats.sd_db:.2f} dB over four 4 MS/s runs", "TX-ON/OFF"),
        MatrixRow("Streaming sanity", "43.76 dB at 2 MS/s", "rate check"),
        MatrixRow("Artifact-aware result", f"TX-ON remains near hop-grid proxy bin ({peak_mhz:.4f} MHz)", "DC/LO mask"),
        MatrixRow("Safety / boundary", "no clipping/saturation; no packet decode, PER/PDR, or OTA", "scope"),
    ]


def draw_matrix(canvas: Canvas, rect: Rect, rows: list[MatrixRow]) -> None:
    draw_text(canvas, rect.x, rect.y + rect.h - 8, "B  Evidence matrix", 7.2, True)
    table = Rect(rect.x, rect.y + 2, rect.w, rect.h - 15)
    round_box(canvas, table, white)
    header_h = 12
    row_h = (table.h - header_h) / len(rows)
    col1 = 53
    col2 = 148
    col3 = table.w - col1 - col2
    canvas.setFillColor(PALE_BLUE)
    canvas.rect(table.x, table.y + table.h - header_h, table.w, header_h, stroke=0, fill=1)
    draw_text(canvas, table.x + 4, table.y + table.h - 8, "Check", 5.8, True, BLUE)
    draw_text(canvas, table.x + col1 + 4, table.y + table.h - 8, "Observed evidence", 5.8, True, BLUE)
    draw_text(canvas, table.x + col1 + col2 + 4, table.y + table.h - 8, "Boundary", 5.8, True, BLUE)
    canvas.setStrokeColor(LINE)
    canvas.line(table.x + col1, table.y, table.x + col1, table.y + table.h)
    canvas.line(table.x + col1 + col2, table.y, table.x + col1 + col2, table.y + table.h)
    y = table.y + table.h - header_h
    for idx, row in enumerate(rows):
        y -= row_h
        if idx % 2 == 1:
            canvas.setFillColor(HexColor("#FAFAFA"))
            canvas.rect(table.x, y, table.w, row_h, stroke=0, fill=1)
        canvas.setStrokeColor(LINE)
        canvas.line(table.x, y, table.x + table.w, y)
        draw_text(canvas, table.x + 4, y + row_h / 2 - 2, row.label, 5.15, True)
        draw_text(canvas, table.x + col1 + 4, y + row_h / 2 - 2, row.evidence, 4.85)
        draw_text(canvas, table.x + col1 + col2 + 4, y + row_h / 2 - 2, row.boundary, 4.95, False, GRAY)


def draw_trace(canvas: Canvas, rect: Rect,
               summary: dict[str, float | bool | str | list[str]]) -> None:
    draw_text(canvas, rect.x, rect.y + rect.h - 8, "C  Supporting trace", 7.2, True)
    image_rect = Rect(rect.x + 66, rect.y + 4, rect.w - 72, rect.h - 18)
    with Image.open(RUN / "artifact_masked_maxhold_txon_vs_noise.png") as image:
        crop = image.crop((58, 75, image.width - 18, image.height - 38))
        canvas.drawImage(ImageReader(crop), image_rect.x, image_rect.y,
                         width=image_rect.w, height=image_rect.h,
                         preserveAspectRatio=True, anchor="c")
    delta = float(summary["txon_minus_txoff_db_after_mask"])
    draw_text(canvas, rect.x + 4, rect.y + 24, "artifact-masked", 5.7, True, RED)
    draw_text(canvas, rect.x + 4, rect.y + 15, "TX-ON/TX-OFF", 5.5, False, GRAY)
    draw_text(canvas, rect.x + 4, rect.y + 6, f"{delta:.1f} dB visible", 5.5, False, GRAY)


def main() -> None:
    repeats = repeat_stats()
    controls = control_stats()
    summary = artifact_summary()
    canvas = Canvas(str(OUT_PDF), pagesize=landscape((3.55 * 72, 3.10 * 72)))
    width, height = landscape((3.55 * 72, 3.10 * 72))
    margin = 7
    gap = 5
    usable_w = width - 2 * margin
    protocol_h = 56
    trace_h = 52
    matrix_h = height - 2 * margin - 2 * gap - protocol_h - trace_h
    protocol = Rect(margin, height - margin - protocol_h, usable_w, protocol_h)
    matrix = Rect(margin, protocol.y - gap - matrix_h, usable_w, matrix_h)
    trace = Rect(margin, margin, usable_w, trace_h)
    draw_protocol(canvas, protocol)
    draw_matrix(canvas, matrix, matrix_rows(repeats, controls, summary))
    draw_trace(canvas, trace, summary)
    canvas.showPage()
    canvas.save()


if __name__ == "__main__":
    main()
