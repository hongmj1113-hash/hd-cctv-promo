"""Build Meta ad creatives from the landing images.

feed  : 1080x1350 (4:5)  - image fit to full height, blurred extension on the sides
story : 1080x1920 (9:16) - image fit inside the Stories/Reels safe zone
        (top ~250px and bottom ~340px are covered by app UI), blurred fill around it
Usage: python3 make_creatives.py <img_dir> <out_dir>
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

SRC = {  # ad key -> source file
    "A_price": "01.gif",
    "B_card": "06.jpg",
    "C_security": "04.jpg",
}


def load(path: Path) -> Image.Image:
    im = Image.open(path)
    if getattr(im, "n_frames", 1) > 1:
        im.seek(im.n_frames - 1)  # GIF counter ends on its final value
    return im.convert("RGB")


def backdrop(im: Image.Image, size) -> Image.Image:
    W, H = size
    s = max(W / im.width, H / im.height)
    bg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(40))
    return ImageEnhance.Brightness(bg).enhance(0.9)


def place(im, size, box):
    """Fit im inside box=(x, y, w, h) on a blurred backdrop of `size`."""
    x, y, w, h = box
    s = min(w / im.width, h / im.height)
    fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    out = backdrop(im, size)
    out.paste(fg, (x + (w - fg.width) // 2, y + (h - fg.height) // 2))
    return out


def main(img_dir, out_dir):
    img_dir, out_dir = Path(img_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, fname in SRC.items():
        im = load(img_dir / fname)
        place(im, (1080, 1350), (0, 0, 1080, 1350)).save(out_dir / f"{key}_feed.jpg", quality=90)
        place(im, (1080, 1920), (0, 250, 1080, 1920 - 250 - 340)).save(out_dir / f"{key}_story.jpg", quality=90)
    print(sorted(p.name for p in out_dir.iterdir()))


if __name__ == "__main__":
    main(*sys.argv[1:3])
