"""Domain constants for the field management application."""

from __future__ import annotations

# Ordered configuration of the sports categories displayed across the site.
# Each tuple represents ``(slug, human_readable_name)``.
CATEGORY_DEFINITIONS: list[tuple[str, str]] = [
    ("padel", "Padel"),
    ("tennis", "Tennis"),
    ("badminton", "Badminton"),
    ("basket", "Basket"),
    ("sepak-bola", "Sepak Bola"),
    ("mini-soccer", "Mini Soccer"),
    ("futsal", "Futsal"),
    ("billiard", "Billiard"),
    ("tenis-meja", "Tenis Meja"),
    ("volly-ball", "Volly Ball"),
]


# Convenience mappings derived from ``CATEGORY_DEFINITIONS`` to avoid
# recomputing them in multiple modules.
CATEGORY_SLUG_SEQUENCE: list[str] = [slug for slug, _ in CATEGORY_DEFINITIONS]
CATEGORY_NAME_MAP: dict[str, str] = dict(CATEGORY_DEFINITIONS)
