# Sundarakala website: notes for Claude

Static site for Sundarakala, a Madras (Chennai) folk-art studio run by the artist Prasannavika.
Hosted on GitHub Pages at https://sundarakala.com (see `CNAME`). There is no build step, framework or backend:
plain HTML files with inline CSS and a little inline JS. Pushing to `master` deploys.

## Files

- `index.html`: landing page. A single centred card (logo, wordmark, bio, WhatsApp + Instagram buttons) with a
  "Now available: totes" callout above it that links to `totes.html`.
- `totes.html`: the tote shop. Static product cards, WhatsApp "buy" links, sold-out styling, and a `<dialog>` lightbox.
- `assets/logo.png`: lotus logo, also the favicon and OG image.
- `assets/autography-wordmark.woff2`: a subset of the licensed Autography font with only the "Sundarakala" glyphs.
  Use it **only** for the wordmark. The full `assets/Autography.otf` is gitignored and must never be committed.
- `assets/totes/shop/<slug>.jpg` (1200×1500) and `<slug>-640.jpg` (640×800): processed tote photos.
- `tools/tote_photos.py`: the photo pipeline (see below).
- `_config.yml`: keeps `README.md`, `CLAUDE.md` and `tools/` off the published site. GitHub Pages runs Jekyll,
  so add any new non-site files to its `exclude` list.
- `DESIGN_BRIEF.md`, `brief.txt`: brand and design brief plus the About text. **Gitignored** and local only;
  read them for tone and brand context.

## Design system (keep consistent)

- **Light mode only.** Never add a dark theme.
- Colour tokens are on `:root` in each page: `--cream #FBF6EE` (page), `--card #FDFAF3`, `--ink #1a1310`,
  `--body #4a3d33`, `--muted #6b5d4d`, `--red #C00A0D`, `--red-dark #AC0A0D`.
- Type: **Spectral** (Google Fonts) for everything, and **Autography** for the red "Sundarakala" wordmark only.
  Small labels: 11px, uppercase, `letter-spacing: .28em`, muted.
- Motifs: a 2px red rule plus a 7px "ticks" rule (repeating-gradient) at the top and bottom of the page; 1.5px ink
  borders on cards; pill buttons (`border-radius: 999px`); a short 54×2px red divider.
- Mobile first: the audience comes from Instagram. Use a 16px side gutter and no horizontal scroll at 375px.
- Each page is self-contained (its CSS is duplicated, not shared). That's deliberate for a two-page site.

## Totes (`totes.html`)

- Price **₹1,499 including shipping** for every tote.
- Card title format: **`Name · Colour`**. When one design has two cream versions, the strap colour goes into the
  colour ("Cream & Green"). Both colours of a design sit next to each other in the grid.
- The current names (Mithila Muse, Golden Fish, Kali, …) were chosen by Claude as placeholders. The owner may
  rename them. To rename, update the `<h2 class="name">`, the image `alt`, **and** the WhatsApp message in that
  card. The file slug can stay as it is.
- WhatsApp number: `919840288010`. Buy link: `https://wa.me/919840288010?text=<urlencoded>`, with the message
  `Hey, I'd like to buy the <Name> · <Colour> tote`.
- **Sold out:** change `<article class="product">` to `<article class="product sold-out">`. CSS adds the diagonal
  banner, strikes through the price and greys the photo. JS turns the buy button into a disabled "Sold out"
  label. The lightbox picks it up automatically.
- The lightbox is a native `<dialog>` built from the cards at runtime (photo `href` = full image, plus cloned
  name, price and buy button). It handles arrows, swipe and Esc, and focus goes back to the card on close.
  Without JS, the photo link still opens the image.

### Adding a new tote

1. Get the raw photo. Totes were shot top-down on a white marble floor, 960×1280.
2. Run from the repo root:
   `uv run tools/tote_photos.py PHOTO SLUG "Name" "Colour" [...more groups of 4]`
   This removes the background (rembg + **BiRefNet**, which handles cream canvas on white marble; u2net did not),
   colour-corrects, centres the tote on a 4:5 canvas tinted with its strap colour (the owner chose
   "strap tint"), writes both sizes to `assets/totes/shop/`, and prints the card HTML on stdout.
   The first run downloads a ~1 GB model.
3. Paste the card into the `.grid` section next to its sibling colour. Update `aria-label="N totes"` on the grid,
   and the "10 designs" count in the `index.html` callout if the number of designs changed.
4. Look at the output image before committing. If a tote has a lot of white close to the floor colour, check
   the edges at full size.

Raw photos are not kept in the repo; the owner deleted them after processing.

## Working conventions

- Python: always use `uv` (scripts carry inline `# /// script` dependencies).
- In this shell, `rm` is aliased to `rm -i` and will hang on a prompt. Use `/bin/rm`.
- Preview: `open <file>.html`. Screenshots: headless Chrome,
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --virtual-time-budget=4000 --window-size=1280,1000 --screenshot=out.png file://$PWD/totes.html`.
  Headless Chrome won't go narrower than about 500px, so for phone width put the page in a
  `<iframe style="width:390px">` inside a scratch HTML file and add `--allow-file-access-from-files`.
- Write HTML the user will look at into the repo, not a scratch directory, and don't publish it as a claude.ai artifact.
- **Commit and push only when asked.** The owner asks for each one explicitly. Work directly on `master`.
