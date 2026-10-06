"""Deterministic local OCR for images supplied by the governed service layer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

import numpy as np
from PIL import Image


ENGINE_NAME = "rapidocr-onnxruntime"
MODEL_PROFILE = "PP-OCRv6-small-pt"
OCR_PARAMETERS = {
    "Det.engine_type": "onnxruntime",
    "Det.lang_type": "ch",
    "Det.model_type": "small",
    "Det.ocr_version": "PP-OCRv6",
    "Rec.engine_type": "onnxruntime",
    # PP-OCRv6 small uses one multilingual recognition model; it includes pt.
    "Rec.lang_type": "ch",
    "Rec.model_type": "small",
    "Rec.ocr_version": "PP-OCRv6",
}


def _package_version() -> str:
    try:
        return version("rapidocr")
    except PackageNotFoundError:
        return "unavailable"


ENGINE_VERSION = _package_version()
PARAMETERS_JSON = json.dumps(
    {"language": "pt", "model_profile": MODEL_PROFILE, **OCR_PARAMETERS},
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)


class OCRExecutionError(Exception):
    """Raised when the local OCR engine fails technically."""


@dataclass(frozen=True)
class OCRTextResult:
    raw_text: str
    text_obtained: bool
    engine: str
    engine_version: str
    model_profile: str
    parameters_json: str


@lru_cache(maxsize=1)
def _get_engine():
    from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR

    return RapidOCR(
        params={
            "Det.engine_type": EngineType.ONNXRUNTIME,
            "Det.lang_type": LangDet.CH,
            "Det.model_type": ModelType.SMALL,
            "Det.ocr_version": OCRVersion.PPOCRV6,
            "Rec.engine_type": EngineType.ONNXRUNTIME,
            "Rec.lang_type": LangRec.CH,
            "Rec.model_type": ModelType.SMALL,
            "Rec.ocr_version": OCRVersion.PPOCRV6,
        }
    )


def extract_ocr_image(image: Image.Image) -> OCRTextResult:
    """Run local OCR on an in-memory image already authorized by the caller."""
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image")

    rgb = np.asarray(image.convert("RGB"))
    bgr = np.ascontiguousarray(rgb[:, :, ::-1])
    try:
        result = _get_engine()(bgr)
        texts = getattr(result, "txts", None) or ()
    except Exception as exc:
        raise OCRExecutionError("Local OCR execution failed.") from exc

    normalized_lines = [str(item).strip() for item in texts if str(item).strip()]
    raw_text = "\n".join(normalized_lines)
    return OCRTextResult(
        raw_text=raw_text,
        text_obtained=bool(raw_text),
        engine=ENGINE_NAME,
        engine_version=ENGINE_VERSION,
        model_profile=MODEL_PROFILE,
        parameters_json=PARAMETERS_JSON,
    )
