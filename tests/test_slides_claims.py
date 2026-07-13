import re
import shutil
import subprocess
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[1]
SLIDE_TEX: Final = ROOT / "paper" / "slides_overview.tex"
SLIDE_PDF: Final = ROOT / "paper" / "slides_overview.pdf"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _pdf_text(path: Path) -> str:
    assert path.exists(), path
    pdftotext = shutil.which("pdftotext")
    assert pdftotext is not None
    result = subprocess.run(
        [pdftotext, str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip()
    return result.stdout


def _normalized_pdf_text(path: Path) -> str:
    return " ".join(_pdf_text(path).split())


def test_pdf_has_twelve_main_slides_and_two_backups() -> None:
    result = subprocess.run(
        ["pdfinfo", str(SLIDE_PDF)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert re.search(r"^Pages:\s+14$", result.stdout, flags=re.MULTILINE) is not None


def test_no_logo_or_conducted_iq_content_is_referenced() -> None:
    source = _read(SLIDE_TEX)
    rendered = _pdf_text(SLIDE_PDF)
    combined = f"{source}\n{rendered}"

    forbidden_fragments = (
        "nthu_logo",
        "NTHU",
        "conducted-IQ",
        "Conducted-IQ",
        "conducted IQ",
        "TX-ON",
        "TX-OFF",
        "waveform",
        "spectrum",
        "fig_conducted_iq_setup",
        "fig_hw_conducted_iq_txon_txoff",
    )
    for fragment in forbidden_fragments:
        assert fragment not in combined


def test_no_forbidden_validation_or_hardware_wording() -> None:
    combined = f"{_read(SLIDE_TEX)}\n{_pdf_text(SLIDE_PDF)}"
    forbidden_case_insensitive = (
        r"\bLR1131\b",
        r"\bCFO\b",
        r"\bhop-center\b",
        r"\bgateway\b",
        r"\blive-satellite\b",
        r"\blive link\b",
        r"\blink validation\b",
        r"\blink-layer validation\b",
        r"\bpacket success\b",
    )
    forbidden_exact = (
        r"\bPER\b",
        r"\bPDR\b",
        r"\bCRC\b",
        r"\bACK\b",
        r"\bOTA\b",
    )

    for pattern in forbidden_case_insensitive:
        assert re.search(pattern, combined, flags=re.IGNORECASE) is None, pattern
    for pattern in forbidden_exact:
        assert re.search(pattern, combined) is None, pattern


def test_required_claim_boundaries_are_present() -> None:
    source = _read(SLIDE_TEX)
    rendered = _normalized_pdf_text(SLIDE_PDF)
    combined = f"{source}\n{rendered}"
    required_fragments = (
        "All real results are model-derived inter-TLE residuals.",
        "reference_is_measured_truth=false",
        "no measured Doppler truth",
        "Controlled software-only check.",
        "Software-only control proxy; not a packet result.",
        "not a BLACK KITE improvement",
    )

    for fragment in required_fragments:
        assert fragment in combined, fragment


def test_main_contribution_order_begins_with_real_negative_finding() -> None:
    source = _read(SLIDE_TEX)
    ordered_markers = (
        r"\item \textbf{Real-data negative finding.}",
        r"\item \textbf{Chronological evidence-gated deploy/no-deploy rule.}",
        r"\item \textbf{Software-only endpoint proxy with explicit limits.}",
    )
    positions = [source.index(marker) for marker in ordered_markers]

    assert positions == sorted(positions)


def test_story_order_places_real_result_before_synthetic_and_proxy() -> None:
    text = _normalized_pdf_text(SLIDE_PDF)
    ordered_markers = (
        "Main Real Result",
        "Why a Closed Gate Matters",
        "Controlled Synthetic Mechanism Check",
        "Endpoint Implications",
        "Limitations and Next Campaign",
    )
    positions = [text.index(marker) for marker in ordered_markers]

    assert positions == sorted(positions)
