import io

import pytest
from PIL import Image

from app.services import pdf_service


def _png(w=10, h=10) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 100, 50)).save(buf, format="PNG")
    return buf.getvalue()


def test_image_passthrough_returns_one_png():
    pages = pdf_service.to_png_pages(_png(), "image/png")
    assert len(pages) == 1
    with Image.open(io.BytesIO(pages[0])) as im:
        assert im.format == "PNG"


def test_oversized_image_downscaled():
    pages = pdf_service.to_png_pages(_png(3000, 1000), "image/png")
    with Image.open(io.BytesIO(pages[0])) as im:
        assert max(im.size) <= 1600


def test_unreadable_bytes_raise_value_error():
    with pytest.raises(ValueError):
        pdf_service.to_png_pages(b"not-an-image", "image/png")


def test_is_pdf_detection():
    assert pdf_service.is_pdf(b"%PDF-1.7 ...")
    assert not pdf_service.is_pdf(_png())
