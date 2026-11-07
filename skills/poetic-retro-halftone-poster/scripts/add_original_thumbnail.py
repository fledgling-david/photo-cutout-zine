#!/usr/bin/env python3
"""Add an uncropped, proportionally scaled original-photo thumbnail to a 3:4 poster.

The generated poster must leave a clear reserved area in its upper-right corner.
The source photo is only resized to fit; it is not cropped or color-corrected.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_label_font(font_path: str | None, size: int) -> ImageFont.ImageFont:
    if font_path:
        return ImageFont.truetype(font_path, size=size)
    try:
        return ImageFont.truetype("DejaVuSansMono.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def add_thumbnail(
    base_path: Path,
    original_path: Path,
    output_path: Path,
    font_path: str | None = None,
    overwrite: bool = False,
) -> tuple[int, int]:
    for path in (base_path, original_path):
        if not path.is_file():
            raise FileNotFoundError(f"Input image not found: {path}")

    if output_path.resolve() in {base_path.resolve(), original_path.resolve()}:
        raise ValueError("Output must be a new file; it cannot overwrite either input.")
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. Use --overwrite to replace it."
        )
    if output_path.suffix.lower() != ".png":
        raise ValueError("Output must use the .png extension.")

    with Image.open(base_path) as opened:
        poster = ImageOps.exif_transpose(opened).convert("RGB")

    width, height = poster.size
    ratio = width / height
    if abs(ratio - 0.75) > 0.005:
        raise ValueError(
            f"Base poster must already be 3:4 (within 0.005 tolerance); got {width}x{height}."
        )

    with Image.open(original_path) as opened:
        original = ImageOps.exif_transpose(opened).convert("RGB")

    # The thumbnail is kept whole. Its dimensions are bounded by both width
    # and height so tall originals still fit inside the upper paper area.
    max_thumb_width = max(1, round(width * 0.17))
    max_thumb_height = max(1, round(height * 0.20))
    thumbnail = ImageOps.contain(
        original,
        (max_thumb_width, max_thumb_height),
        method=Image.Resampling.LANCZOS,
    )

    margin = max(4, round(width * 0.035))
    border = max(1, round(width * 0.0015))
    label_gap = max(3, round(height * 0.006))
    label_size = max(10, round(height * 0.012))
    label = "ORIGINAL"
    font = load_label_font(font_path, label_size)

    draw = ImageDraw.Draw(poster)
    bbox = draw.textbbox((0, 0), label, font=font)
    label_width = bbox[2] - bbox[0]
    label_height = bbox[3] - bbox[1]

    frame_width = thumbnail.width + border * 2
    frame_height = thumbnail.height + border * 2
    x = width - margin - frame_width
    y = margin

    # Warm-paper backing and a fine dark-ink frame; no shadow or extra badge.
    paper = (250, 247, 238)
    ink = (55, 49, 44)
    draw.rectangle(
        (x, y, x + frame_width - 1, y + frame_height - 1),
        fill=paper,
        outline=ink,
        width=border,
    )
    poster.paste(thumbnail, (x + border, y + border))

    label_x = x + (frame_width - label_width) // 2 - bbox[0]
    label_y = y + frame_height + label_gap - bbox[1]
    draw.text((label_x, label_y), label, fill=ink, font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    poster.save(output_path, format="PNG", optimize=True)
    return poster.size


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Overlay the complete original photo as the poster's ORIGINAL thumbnail."
    )
    parser.add_argument("--base", required=True, type=Path, help="Generated 3:4 poster PNG or image.")
    parser.add_argument("--original", required=True, type=Path, help="Original uploaded photograph.")
    parser.add_argument("--output", required=True, type=Path, help="New output PNG path.")
    parser.add_argument("--font", help="Optional local TTF/OTF font for the ORIGINAL label.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file (never replaces either input).",
    )
    args = parser.parse_args()

    try:
        size = add_thumbnail(
            args.base,
            args.original,
            args.output,
            font_path=args.font,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        parser.error(str(exc))

    print(f"Saved {args.output} ({size[0]}x{size[1]}); original thumbnail is uncropped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
