#!/usr/bin/env python3
"""Compose a photo cut-out zine without regenerating any photo pixels.

Requires Pillow. Copy and typography are supplied by the observing agent.
Run with --help for file arguments; see references/exact-composition.md.
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
import random
import re
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


GRAY = (66, 65, 61)
RED = (126, 57, 51)
IVORY = (246, 240, 227)
RESAMPLE = Image.Resampling.LANCZOS


def words(value):
    return re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", value)


def text_value(value, field):
    if not isinstance(value, str) or not value.strip() or "\n" in value:
        raise ValueError(f"{field} must be one nonempty line")
    return value.strip()


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("Config must be a JSON object")
    title = text_value(config.get("title"), "title")
    if not 2 <= len(words(title)) <= 3:
        raise ValueError("Title must contain 2-3 English words")
    config["title"] = title
    for key, count in (("poem_lines", 2), ("micro_lines", 5)):
        lines = config.get(key)
        if not isinstance(lines, list) or len(lines) != count:
            raise ValueError(f"{key} must contain exactly {count} lines")
        config[key] = [text_value(line, key) for line in lines]
    if not 8 <= len(words(" ".join(config["poem_lines"]))) <= 12:
        raise ValueError("Poem must contain 8-12 English words in total")
    date = text_value(config.get("date"), "date")
    try:
        parsed = datetime.strptime(date.replace(" ", ""), "%m.%d.%Y")
    except ValueError as exc:
        raise ValueError("Date must be a real date in MM. DD. YYYY format") from exc
    config["date"] = parsed.strftime("%m. %d. %Y")
    paths = config.get("sketch_paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("Provide sketch_paths based on a motif in the actual photo")
    for path in paths:
        if not isinstance(path, list) or len(path) < 2:
            raise ValueError("Each sketch path needs at least two points")
        for point in path:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError("Sketch points must be [x, y] pairs")
            if not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in point):
                raise ValueError("Sketch coordinates must be numbers in [0, 1]")
    box = config.get("crop_box", [0, 0, 1, 1])
    if not isinstance(box, list) or len(box) != 4:
        raise ValueError("crop_box must be [left, top, right, bottom]")
    if not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in box):
        raise ValueError("Crop coordinates must be numbers in [0, 1]")
    if box[0] >= box[2] or box[1] >= box[3]:
        raise ValueError("Crop box must have positive width and height")
    config["crop_box"] = box
    return config


def serif(size, explicit=None):
    if explicit:
        candidates = [explicit]
    else:
        candidates = [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "DejaVuSerif.ttf",
        ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), max(1, int(size)))
        except OSError:
            continue
    raise ValueError("No serif font found; pass an existing font file with --font")


def paper(size):
    rng = random.Random(3817)
    grain = Image.frombytes("L", size, rng.randbytes(size[0] * size[1]))
    channels = [grain.point([min(255, max(0, c + round((v - 128) / 80)))
                            for v in range(256)]) for c in IVORY]
    return Image.merge("RGB", channels)


def perforation_mask(size, canvas_width):
    scale = 4
    width, height = (v * scale for v in size)
    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)
    radius = max(2, round(canvas_width * 0.0032)) * scale
    for extent, horizontal in ((width, True), (height, False)):
        count = max(3, round(extent / (3.3 * radius)))
        for index in range(count):
            pos = round((index + 0.5) * extent / count)
            centers = ((pos, 0), (pos, height)) if horizontal else ((0, pos), (width, pos))
            for x, y in centers:
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=0)
    return mask.resize(size, RESAMPLE)


def fitted_text(draw, xy, text, px, max_width, font_path, color):
    font = serif(px, font_path)
    while draw.textlength(text, font=font) > max_width and px > 7:
        px -= 1
        font = serif(px, font_path)
    if draw.textlength(text, font=font) > max_width:
        raise ValueError("Text is too long for the quiet caption area; shorten it")
    draw.text(xy, text, fill=color, font=font, anchor="lt")


def decorate(canvas, config, font_path):
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    fitted_text(draw, (width * .06, height * .555), config["date"],
                round(width * .013), width * .42, font_path, GRAY)
    fitted_text(draw, (width * .06, height * .882), config["title"],
                round(width * .020), width * .50, font_path, RED)
    for i, line in enumerate(config["poem_lines"]):
        fitted_text(draw, (width * .06, height * (.915 + .018 * i)), line,
                    round(width * .0125), width * .50, font_path, GRAY)
    for i, line in enumerate(config["micro_lines"]):
        fitted_text(draw, (width * .81, height * (.886 + .0115 * i)), line,
                    round(width * .0068), width * .14, font_path, GRAY)
    # Draw only the observed motif, supplied as a few normalized polylines.
    sw, sh = round(width * .12), round(height * .078)
    scale = 4
    sketch = Image.new("RGBA", (sw * scale, sh * scale))
    pen = ImageDraw.Draw(sketch)
    for path in config["sketch_paths"]:
        points = [(round(x * (sw * scale - 1)), round(y * (sh * scale - 1))) for x, y in path]
        pen.line(points, fill=GRAY + (230,), width=max(2, round(width * .0008 * scale)), joint="curve")
    sketch = sketch.resize((sw, sh), RESAMPLE)
    canvas.paste(sketch, (round(width * .655), round(height * .875)), sketch)


def same_under_mask(actual, expected, mask, label):
    diff = ImageChops.difference(actual, expected)
    selected = ImageChops.multiply(diff, Image.merge("RGB", (mask, mask, mask)))
    if selected.getbbox() is not None:
        raise RuntimeError(f"Pixel verification failed: {label}")


def compose(image_path, config, output_path, width=1536, font_path=None):
    if width < 600 or width > 6000 or width % 6:
        raise ValueError("Width must be a multiple of 6 between 600 and 6000")
    height = width * 4 // 3
    half = height // 2
    config = validate_config(config)
    image_path, output_path = Path(image_path), Path(output_path)
    if output_path.suffix.lower() != ".png":
        raise ValueError("Use PNG output for lossless pixel verification")
    if image_path.resolve() == output_path.resolve():
        raise ValueError("Output must not overwrite the source photograph")
    if output_path.exists():
        raise ValueError("Output already exists; choose a new versioned filename")
    with Image.open(image_path) as raw:
        source = ImageOps.exif_transpose(raw).convert("RGB")
    source_size = source.size
    x0, y0, x1, y1 = config["crop_box"]
    crop = (round(x0 * source.width), round(y0 * source.height),
            round(x1 * source.width), round(y1 * source.height))
    if crop[2] <= crop[0] or crop[3] <= crop[1]:
        raise ValueError("Crop box collapses to zero pixels in this image")
    top = ImageOps.fit(source.crop(crop), (width, half), method=RESAMPLE)
    sheet = paper((width, height))
    canvas = sheet.copy()
    canvas.paste(top, (0, 0))
    # Even sizes make both centers exact on the pixel lattice.
    stamp_width = round(width * .23 / 2) * 2
    stamp_height = round(half * .38 / 2) * 2
    sx = (width - stamp_width) // 2
    sy = (half - stamp_height) // 2
    upper_box = (sx, sy, sx + stamp_width, sy + stamp_height)
    lower_box = (sx, sy + half, sx + stamp_width, sy + half + stamp_height)
    extracted = top.crop(upper_box)
    mask = perforation_mask(extracted.size, width)
    canvas.paste(sheet.crop(upper_box), upper_box[:2], mask)
    canvas.paste(extracted, lower_box[:2], mask)
    decorate(canvas, config, font_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG")

    # Reopen what was actually written; verify both opaque pixels and all edge blends.
    with Image.open(output_path) as saved:
        result = saved.convert("RGB")
    if result.size != (width, height):
        raise RuntimeError("Unexpected saved dimensions")
    opaque = mask.point(lambda v: 255 if v == 255 else 0)
    same_under_mask(result.crop(lower_box), extracted, opaque, "lower stamp crop")
    same_under_mask(result.crop(upper_box), sheet.crop(upper_box), opaque, "blank upper hole")
    expected_top = top.copy()
    expected_top.paste(sheet.crop(upper_box), upper_box[:2], mask)
    if ImageChops.difference(result.crop((0, 0, width, half)), expected_top).getbbox():
        raise RuntimeError("Upper photo or cut-out edge changed")
    expected_lower = sheet.crop(lower_box)
    expected_lower.paste(extracted, (0, 0), mask)
    if ImageChops.difference(result.crop(lower_box), expected_lower).getbbox():
        raise RuntimeError("Lower stamp or perforation edge changed")
    return {
        "output": str(output_path.resolve()),
        "size": [width, height],
        "oriented_source_size": list(source_size),
        "source_crop_pixels": list(crop),
        "upper_box": list(upper_box),
        "lower_box": list(lower_box),
        "pixel_verification": "passed",
        "fidelity_scope": "source photo after crop/scale, shared perforation mask",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--config", required=True, help="JSON selected by the observing agent")
    parser.add_argument("--output", required=True, help="New PNG file; never overwrites existing files")
    parser.add_argument("--width", type=int, default=1536)
    parser.add_argument("--font", help="Existing serif TTF/OTF on this system")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
        result = compose(args.image, config, args.output, args.width, args.font)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
