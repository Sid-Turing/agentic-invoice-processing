"""Render document bytes to PNG image bytes for the vision model."""
from __future__ import annotations

import io

_MAX_DIM = 1600
_PDF_MAGIC = b"%PDF"


def _downscale_png(image_bytes: bytes) -> bytes:
    from PIL import Image

    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > _MAX_DIM:
            scale = _MAX_DIM / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()


def is_pdf(data: bytes) -> bool:
    return data[:4] == _PDF_MAGIC


def to_png_pages(data: bytes, mime: str | None = None) -> list[bytes]:
    """Return one PNG blob per page. PDFs are rendered at 300 dpi; images are
    re-encoded/downscaled to PNG. Raises ValueError on unreadable input."""
    if is_pdf(data) or (mime or "").endswith("pdf"):
        from pdf2image import convert_from_bytes

        try:
            # Render to PPM (poppler's default), NOT PNG: some poppler builds have a
            # libpng version clash in their PNG writer. Pillow re-encodes to PNG below
            # using its own bundled libpng, avoiding the system dependency entirely.
            pages = convert_from_bytes(data, dpi=300)
        except Exception as exc:  # poppler failure / corrupt pdf
            raise ValueError(f"could not render PDF: {exc}") from exc
        result = []
        for page in pages:
            buf = io.BytesIO()
            page.save(buf, format="PNG")
            result.append(_downscale_png(buf.getvalue()))
        if not result:
            raise ValueError("PDF produced no pages")
        return result

    try:
        return [_downscale_png(data)]
    except Exception as exc:
        raise ValueError(f"could not read image: {exc}") from exc
