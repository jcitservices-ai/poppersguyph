from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WATERMARK_TEXT = "@PoppersGuyPH"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
IGNORED_DIRS = {".git", "originals_before_watermark", "__pycache__"}


def load_font(image_width: int) -> ImageFont.ImageFont:
    font_size = max(22, image_width // 18)
    for font_path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(font_path, font_size)
        except OSError:
            continue

    return ImageFont.load_default()


def apply_watermark(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    font = load_font(image.width)
    margin = max(18, image.width // 40)
    stroke_width = max(2, image.width // 500)

    text_bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font, stroke_width=stroke_width)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (image.width - text_width) / 2
    y = (image.height - text_height) / 2

    # Centered overlay with stronger backing so the mark sits over the product clearly.
    padding_x = max(18, image.width // 40)
    padding_y = max(12, image.height // 55)
    draw.rounded_rectangle(
        (
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            y + text_height + padding_y,
        ),
        radius=max(12, image.width // 60),
        fill=(0, 0, 0, 120),
    )

    draw.text(
        (x, y),
        WATERMARK_TEXT,
        font=font,
        fill=(255, 255, 255, 210),
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0, 180),
    )

    composited = Image.alpha_composite(image, overlay)
    save_format = "PNG" if image_path.suffix.lower() == ".png" else "JPEG"
    if save_format == "JPEG":
        composited = composited.convert("RGB")
        composited.save(image_path, format=save_format, quality=92, optimize=True)
    else:
        composited.save(image_path, format=save_format, optimize=True)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    image_paths = sorted(
        path
        for path in repo_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not any(part in IGNORED_DIRS for part in path.parts)
    )

    for image_path in image_paths:
        apply_watermark(image_path)
        print(f"Watermarked {image_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
