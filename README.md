# sundarakala.com

Website for **Sundarakala**, an Indian folk-art studio from Madras. It's plain HTML hosted on GitHub Pages:
push to `master` and the site updates within a minute or two.

| Page | File |
|---|---|
| Home | `index.html` |
| Tote shop | `totes.html` |

## Common changes

### Mark a tote as sold out

In `totes.html`, find the tote's card and change

```html
<article class="product">
```

to

```html
<article class="product sold-out">
```

To put it back on sale, remove ` sold-out`.

### Rename a tote

In that tote's card, change the name in three places: the `<h2 class="name">` heading, the image's `alt` text,
and the WhatsApp message in the `wa.me/...?text=` link (URL-encoded).

### Add a new tote

You need [uv](https://docs.astral.sh/uv/). From the repo folder:

```sh
uv run tools/tote_photos.py path/to/photo.jpg peacock-navy "Peacock" "Navy"
```

This removes the background, adds the tinted backdrop and shadow, saves the images to `assets/totes/shop/`,
and prints the HTML card to paste into `totes.html`. The first run downloads a large (~1 GB) model.

## Notes

- The wordmark font is a licensed subset (`assets/autography-wordmark.woff2`). Don't commit the full font file.
- See `CLAUDE.md` for the design system and more detail.
