# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["rembg[cpu]", "pillow", "numpy"]
# ///
"""Turn a raw tote photo into the shop images used on totes.html.

Removes the background (BiRefNet via rembg), lightly corrects colour, centres
the tote on a 4:5 canvas tinted with a pale wash of its strap colour, adds a
soft shadow, and writes:

    assets/totes/shop/<slug>.jpg       1200x1500 (lightbox / retina)
    assets/totes/shop/<slug>-640.jpg   640x800   (grid)

It then prints a ready-to-paste <article class="product"> card for totes.html.

Usage (from the repo root):

    uv run tools/tote_photos.py PHOTO SLUG "NAME" "COLOUR" [PHOTO SLUG NAME COLOUR ...]

    uv run tools/tote_photos.py ~/Downloads/IMG_1.jpg peacock-navy "Peacock" "Navy"

The first run downloads the BiRefNet model (~1 GB) into ~/.u2net/.
"""
import html
import os
import sys
import urllib.parse

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "totes", "shop")
WHATSAPP = "919840288010"
PRICE = "₹1,499"
WA_ICON = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 18.13h-.01c-1.52 0-3.01-.41-4.3-1.18l-.31-.18-3.2.84.85-3.12-.2-.32a8.2 8.2 0 0 1-1.26-4.36c0-4.54 3.7-8.23 8.24-8.23 2.2 0 4.27.86 5.82 2.42a8.18 8.18 0 0 1 2.41 5.82c0 4.54-3.7 8.23-8.23 8.23zm4.52-6.16c-.25-.12-1.47-.72-1.69-.8-.23-.08-.39-.12-.56.12-.16.25-.64.8-.79.97-.14.16-.29.18-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.14.16-.25.25-.41.08-.16.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.41-.56-.42l-.48-.01c-.16 0-.43.06-.66.31-.23.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.16 1.75 2.67 4.25 3.74.59.26 1.06.41 1.42.52.6.19 1.14.16 1.57.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28z"/></svg>'
W, H = 1200, 1500


def cut_out(path, session):
    from rembg import remove
    return remove(Image.open(path), session=session, post_process_mask=True).convert("RGBA")


def enhance(im):
    rgb, a = im.convert("RGB"), im.getchannel("A")
    rgb = ImageOps.autocontrast(rgb, cutoff=0.5, preserve_tone=True)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.05)
    rgb = ImageEnhance.Color(rgb).enhance(1.08)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.15)
    rgb.putalpha(a)
    return rgb


def fit(im, frac=0.84):
    a = im.getchannel("A").point(lambda v: 0 if v < 12 else v)  # drop faint fringe
    im.putalpha(a)
    im = im.crop(a.getbbox())
    s = min(W * frac / im.width, H * frac / im.height)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def strap_tint(im):
    """Pale background colour taken from the most saturated pixels in the top quarter (the straps)."""
    arr = np.array(im)
    top = arr[: arr.shape[0] // 4]
    px = top[top[..., 3] > 200][:, :3].astype(float)
    sat = px.max(1) - px.min(1)
    px = px[sat > np.percentile(sat, 70)]
    c = np.median(px, 0)
    return tuple(int(v) for v in (c * 0.14 + np.array([250, 246, 240]) * 0.86))


def compose(im):
    bg = Image.new("RGBA", (W, H), strap_tint(im) + (255,))
    x, y = (W - im.width) // 2, (H - im.height) // 2
    a = im.getchannel("A")
    for dy, blur, op in [(6, 6, 0.18), (22, 28, 0.22)]:  # contact shadow + soft drop shadow
        m = Image.new("L", (W, H), 0)
        m.paste(a, (x, y + dy))
        m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
        layer = Image.new("RGBA", (W, H), (40, 30, 20, 255))
        layer.putalpha(m)
        bg.alpha_composite(layer)
    bg.alpha_composite(im, (x, y))
    return bg.convert("RGB")


def card(slug, name, colour):
    title = f"{name} · {colour}"
    msg = f"Hey, I'd like to buy the {title} tote"
    url = f"https://wa.me/{WHATSAPP}?text={urllib.parse.quote(msg)}"
    e = html.escape
    p = f"assets/totes/shop/{slug}"
    return f'''      <article class="product">
        <a class="photo" href="{p}.jpg"><img src="{p}-640.jpg" srcset="{p}-640.jpg 640w, {p}.jpg 1200w" sizes="(min-width: 900px) 340px, (min-width: 520px) 45vw, 92vw" width="640" height="800" loading="lazy" alt="{e(title)} tote bag with a hand-illustrated folk art print"></a>
        <div class="meta">
          <h2 class="name">{e(name)} <span class="sep">·</span> <span class="colour">{e(colour)}</span></h2>
          <p class="price">{PRICE}</p>
        </div>
        <a class="buy" href="{e(url)}" target="_blank" rel="noopener">{WA_ICON} Buy on WhatsApp</a>
      </article>'''


def main(args):
    if not args or len(args) % 4:
        sys.exit(__doc__)
    from rembg import new_session
    session = new_session("birefnet-general")
    os.makedirs(OUT_DIR, exist_ok=True)
    cards = []
    for i in range(0, len(args), 4):
        photo, slug, name, colour = args[i:i + 4]
        img = compose(fit(enhance(cut_out(photo, session))))
        img.save(os.path.join(OUT_DIR, f"{slug}.jpg"), quality=84, optimize=True, progressive=True)
        img.resize((640, 800), Image.LANCZOS).save(
            os.path.join(OUT_DIR, f"{slug}-640.jpg"), quality=82, optimize=True, progressive=True)
        print(f"wrote {slug}.jpg and {slug}-640.jpg", file=sys.stderr)
        cards.append(card(slug, name, colour))
    print("\n".join(cards))


if __name__ == "__main__":
    main(sys.argv[1:])
