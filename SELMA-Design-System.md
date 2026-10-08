# SELMA Zuhause – Design System

Source of truth: the live website selmazuhause.de (`src/style.css`). Use this file as the brief for anything new in the SELMA brand: teasers, social posts, flyers, slides, landing pages.

---

## 1. Brand in one paragraph

SELMA Zuhause is an occupational therapy practice (Ergotherapie) for people with Parkinson's, working only through home visits in Berlin Südost and Charlottenburg. SELMA stands for **„Sicher & Selbstständig im Alltag“**. The look is calm, bright, warm and highly legible: soft mint and peach surfaces, a deep navy for weight and clear teal for action. It should feel like a competent, friendly therapist at your kitchen table, never like a hospital or a tech startup.

**Core line:** Ergotherapie bei Parkinson. Alltag stärken. Stürzen vorbeugen.
**Support line:** Mit Bewegungsroutinen, Hilfsmitteln und Wohnraumanpassung.

### Non-negotiables
1. **Legibility first.** The audience is older adults with Parkinson's (tremor, reduced vision) and their family members. Text is large, contrast is high, and touch targets are big.
2. **Calm, not clinical.** No hospital blue/white, no stock photos of pills or stethoscopes, no alarm red.
3. **Concrete, not fluffy.** Say what happens: "Wir kommen zu Ihnen nach Hause."
4. **German, formal "Sie".** Always address the reader as "Sie", never "du".

---

## 2. Color tokens

```css
:root{
  /* Text & weight */
  --navy:#1c394c;        /* headings, dark sections, strong text */
  --ink:#314c5f;         /* body text */
  --slate:#576d7a;       /* secondary text, captions */
  --royal:#365f7b;       /* logo color, footer background */

  /* Brand teal */
  --teal:#0e9399;        /* decorative + large only (3.6:1 on paper) */
  --teal-strong:#037a7f; /* links, buttons, small accents (5.0:1) */
  --teal-deep:#026a6e;   /* hover / pressed */

  /* Surfaces */
  --mint:#cdeff0;        /* hero, image backgrounds, signature surface */
  --mint-soft:#e6f7f7;   /* chips, icon tiles */
  --mist:#f0f4f5;        /* neutral alternate section */
  --paper:#fcfcfc;       /* page background */
  --white:#ffffff;       /* cards */

  /* Warm accent */
  --peach:#ffb59a;       /* stripes, highlights, focus on dark */
  --peach-soft:#ffeee7;  /* warm section / note background */

  /* Utility */
  --line:#d5e1e4;        /* dividers */
  --field:#6b818d;       /* form field borders */
  --error:#b3261e;
}
```

On dark (navy/royal) backgrounds, body text is `#e8f3f5` (on navy) or `#dbe9ec` (on royal), headings are white and emphasis is peach.

### Usage ratio (approx.)
- 60 % light surfaces: paper, mint, mist
- 25 % text and dark: navy, ink
- 10 % teal: actions, accents
- 5 % peach: decoration, highlights

### Approved pairings (WCAG contrast)

| Text / element | On | Ratio | Use for |
|---|---|---|---|
| navy | paper / mint / peach-soft | 11.8 / 9.9 / 10.7 | headings, anything |
| ink | paper / mint | 8.8 / 7.4 | body text |
| slate | paper | 5.3 | secondary text (not on mint for small text: 4.4) |
| teal-strong | paper / peach-soft | 5.0 / 4.6 | links, small accents |
| teal-strong | mint | 4.2 | **large text only** (≥ 24 px, or ≥ 19 px bold). Use navy or teal-deep for small text on mint |
| teal | any light surface | ≤ 3.6 | **decoration / illustration only, never text** |
| white | teal-strong | 5.1 | primary button |
| white | navy | 12.1 | dark sections |
| peach | navy | 7.1 | emphasis on dark |
| white / #dbe9ec | royal | 6.8 / 5.5 | footer |

---

## 3. Typography

**Typeface:** [Atkinson Hyperlegible Next](https://fonts.google.com/specimen/Atkinson+Hyperlegible+Next). It was designed by the Braille Institute for low-vision readers, which is central to the brand. Free on Google Fonts.
- Weights in use: 400 (body), 700 (labels, buttons, h3/h4), 800 (h1/h2, display)

**Numbers and labels:** [Atkinson Hyperlegible Mono](https://fonts.google.com/specimen/Atkinson+Hyperlegible+Mono) 600, used for phone numbers, step numbers ("1", "2"), prices and times.

```css
--font:"Atkinson Hyperlegible Next",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--mono:"Atkinson Hyperlegible Mono",ui-monospace,Menlo,monospace;
```

### Type scale (mobile → desktop)

| Token | Size | Weight | Line height | Letter spacing |
|---|---|---|---|---|
| display (hero h1) | 36 → 88 px | 800 | 1.0 | -0.035em |
| h1 | 38 → 64 px | 800 | 1.05 | -0.025em |
| h2 | 30 → 48 px | 800 | 1.1 | -0.02em |
| h3 | 22 → 28 px | 700 | 1.2 | -0.015em |
| h4 | 19 → 21 px | 700 | 1.3 | -0.015em |
| lead | 19 → 23 px | 400 | 1.5 | 0 |
| body | 18 → 20 px | 400 | 1.6 | 0 |
| small / fineprint | 16 px | 400 | 1.5 | 0 |
| button / nav / eyebrow | 17 px | 700 | 1.2 | 0.01em |
| footer heading | 17 px, UPPERCASE | 700 | — | 0.06em |

```css
--fs-body:clamp(1.125rem,1.07rem + .25vw,1.25rem);
--fs-lead:clamp(1.1875rem,1.08rem + .5vw,1.4375rem);
--fs-small:1rem;
--fs-h4:clamp(1.1875rem,1.12rem + .3vw,1.3125rem);
--fs-h3:clamp(1.375rem,1.22rem + .7vw,1.75rem);
--fs-h2:clamp(1.875rem,1.45rem + 1.9vw,3rem);
--fs-h1:clamp(2.375rem,1.7rem + 3vw,4rem);
--fs-display:clamp(2.25rem,1.3rem + 5vw,5rem);
```

### Rules
- **Body text is never below 18 px** on screen, and **small text never below 16 px.**
- Headings are navy. A second line or key word may be teal-strong, e.g. "Erst aufbauen, / **dann erhalten.**"
- Keep text measures at **52–66 characters** for body and about 60ch for leads. Balance headline wrapping.
- Don't use italics. Emphasis is bold navy, or peach on dark.
- Don't set long text in all caps. Uppercase is only for small footer labels.
- Write numbers in German format: `9:00 – 18:00 Uhr`, `243 €`, `4.180 €`, `1,3-fach`.

---

## 4. Layout, spacing, shape

```css
--container:1200px;
--gutter:clamp(16px,4vw,40px);
--space-section:clamp(64px,8vw,120px);   /* vertical padding per section */
--header-h:76px;                         /* 68px under 1000px */

--r-media:28px;   /* large images, video, hero */
--r-card:22px;    /* cards, image tiles, CTA bands */
--r-field:14px;   /* inputs */
/* pills: 999px (buttons, chips, nav items) · icon tiles: 16px · notes: 16px · logo tiles: 12px */

--shadow-lift:0 24px 60px -32px rgba(28,57,76,.45);  /* the only big shadow */
--ease-out:cubic-bezier(.16,1,.3,1);
```

- **Generous whitespace.** Sections alternate backgrounds: paper → mint → mist → peach-soft → navy. Never put two dark sections next to each other.
- **Everything is rounded.** There are no sharp image corners.
- **Shadows are soft, long and navy-tinted.** Use them only to lift a white card off a colored surface; never use grey drop shadows.
- Grids: 2 or 3 columns on desktop, 1 column on mobile. Use asymmetric splits for text plus image (about 1.1 : 0.9).

---

## 5. Signature motifs

These make a layout recognisably SELMA. Use at least one per piece.

1. **Peach dash stripes.** A repeating peach bar pattern, used as:
   - **Eyebrow marker:** a 34×12 px block of 6 px peach dashes with 8 px gaps, placed before a teal-strong eyebrow label.
     `repeating-linear-gradient(90deg, #ffb59a 0 6px, transparent 6px 14px)`
   - **Stripe block behind media:** horizontal peach stripes (12 px bar, 18 px gap) on a rounded block offset down and right behind a photo or video.
     `repeating-linear-gradient(180deg, #ffb59a 0 12px, transparent 12px 30px)`
   - **Progress track:** a dashed peach line between step numbers (10 px dash, 16 px gap).
2. **Peach highlighter.** A key phrase is underlined with a thick peach band across the lower 40 % of the text, like a marker stroke.
   `background:linear-gradient(#ffb59a,#ffb59a) 0 calc(100% - .08em)/100% .4em no-repeat`
   Example: "Wir kommen ==zu Ihnen nach Hause==".
3. **Offset mint block.** A mint rounded rectangle sits behind a portrait, offset down-left by about 22 px.
4. **Navy number circles.** Steps are numbered in 64 px navy circles with white mono digits.
5. **Icon tiles.** A 52 px mint-soft rounded square (radius 16) holding a teal-strong line icon.

---

## 6. Components

**Primary button.** A teal-strong pill with white bold text and a round arrow badge on the right.
- Size: min-height 56 px, padding 8 10 8 26 px.
- Arrow badge: 38 px circle in `rgba(255,255,255,.18)` with a 20 px arrow icon.
- Hover: background changes to teal-deep and the arrow nudges 3 px right.

**Secondary (ghost) button.** Transparent with a 2 px navy border and navy text; the arrow badge is mint. On hover it fills navy with white text.

**On dark backgrounds:** use a mint pill with navy text and a navy badge holding a white arrow.

**Card.** White, radius 22, padding 24–44 px, with `--shadow-lift`.

**Chip / tag.** A mint-soft pill with navy 15 px bold text, min-height 44 px.

**Note box.** Peach-soft background, radius 16, padding 16×20, navy bold text.

**CTA band.** Navy, radius 22. Lead text in white bold on the left; a mint button on the right.

**FAQ.** Navy 2 px top rule with line dividers. The plus button is a 44 px mint circle that rotates 45° and turns navy when open.

**Form fields.** 58 px tall with a 2 px `--field` border and radius 14. Labels are always visible above the field, navy bold. Optional fields are marked with "(optional)" in slate.

**Focus.** A 3 px navy outline offset by 3 px; peach on dark backgrounds.

### Common CTA labels (keep the wording)
- "Erstgespräch anfragen"
- "Zu den Leistungen"
- "Rückruf anfordern"
- "Newsletter erhalten"
- "Artikel lesen"

---

## 7. Iconography

- **Style:** line icons (Lucide set), 24 px grid, **1.9 px stroke**, round caps and joins, `fill:none`, colored with `currentColor`.
- **Size:** usually 20–26 px, inside a tile or circle.
- **Color:** teal-strong on mint-soft, navy on mint, or white on navy.
- **Icons in use:** house, award, wallet, heart, arrow, phone, mail, pin, clock, check, plus, user, calendar, play/pause.
- Don't use filled, duotone or emoji-style icons.

---

## 8. Imagery

### Illustrations (primary for concepts)
- Single-weight **dark teal line drawings** (about `#2a6f6c`, close to teal-deep) on a flat **mint** (`#cdeff0`) background, with no fills and no shading.
- Show everyday scenes at home: a person exercising in the living room, a plant, a framed picture, a walker, a grab bar.
- Motion is shown with small curved "swoosh" lines; floor contact or turning circles are drawn as dashed ellipses.
- People are older adults, friendly and active, never frail or in a sickbed.

### Photography
- Bright, airy, natural daylight with soft whites and greys plus one warm accent (orange or brown clothing).
- Real homes: windows, living rooms, bathrooms, hallways. No clinics and no white-coat staging.
- Show older adults (and family) doing things themselves, seen from the side or behind, in calm moments.
- Corners are rounded (22–28 px). Images often sit on a mint tile or with the peach stripe block behind them.

### Avoid
Pills, syringes, hospital beds, wheelchairs as the hero motif, sad or lonely framing, dark moody grading and neon colors.

---

## 9. Logo

- **Files** (in the repo): `src/img/logo.webp` (color), `src/img/logo-white.webp` (on dark) and `src/img/s-mark.webp` (S symbol only, for avatars and favicons).
- **Logo color:** royal `#365f7b`. It is the stacked wordmark "SELMA / Zuhause" with the S-mark on the left. The S-mark is a bold S whose top terminal is a dot, like a head.
- Use it on paper, white or mint. On navy or royal, use the white version.
- **Clear space:** at least the height of the "S" dot on all sides.
- **Minimum height:** 38 px on screen.
- Don't recolor it in teal or peach, don't stretch it, don't add a shadow and don't place it on busy photos.

---

## 10. Motion

- **Easing:** `cubic-bezier(.16,1,.3,1)` (a strong ease-out). Durations are 0.8–1.25 s for reveals and 0.2 s for hovers.
- **Reveals:**
  - Blocks fade up 40 px.
  - Headline words slide up from a mask, staggered by 55 ms per word.
  - Images unveil with a clip-path from the bottom while scaling from 1.22 to 1.
  - Dashed tracks draw in steps.
- Motion is slow and gentle, with no bounce, shake or flashing.
- **Always respect `prefers-reduced-motion`:** show the final state with no motion.

---

## 11. Voice & copy

- **Language:** German, formal "Sie" and gender-inclusive with ":" (Therapeut:innen, Selbstzahler:innen).
- **Tone:** warm, calm, competent and concrete. Use short sentences and active verbs.
- **Patterns from the site:**
  - Three-beat headlines: "Ergotherapie bei Parkinson. Alltag stärken. Stürzen vorbeugen."
  - Two-part contrast: "Erst aufbauen, dann erhalten." / "So früh wie möglich. Nur das, was nötig."
  - Principles: "Erhalten vor kompensieren." / "Vor Ort statt in der Praxis."
- Use the brand term "das SELMA Programm".
- Use "Erstgespräch" for the first contact.
- Use "Menschen mit Parkinson", not "Parkinson-Patienten" or "Betroffene" in headlines.
- Avoid medical promises ("heilt", "garantiert"), fear framing and superlatives.
- **Facts to keep exact:**
  - Hausbesuche in Berlin Südost & Charlottenburg
  - Alle Kassen & privat
  - Phone 030 3758 0867
  - info@selmazuhause.de
  - Mo–Fr 9:00–18:00 Uhr

---

## 12. Applying it to teasers & social

### Formats
- 1080×1080 (feed)
- 1080×1350 (portrait feed)
- 1080×1920 (story/reel; keep text inside the central 1080×1420 safe area)
- 1920×1080 (video/slides)

### Recipe
1. **Background:** mint, or paper for photos, or navy for the closing card.
2. **One headline** in Atkinson Next 800, navy, at least 64 px on 1080 wide, with a maximum of about 8 words. One phrase may get the peach highlighter or turn teal-strong.
3. **One visual:** a teal line illustration or a bright home photo with radius 28 and the peach stripe block behind it.
4. **The eyebrow motif** (peach dashes plus a teal-strong label) as a small kicker, e.g. "Ergotherapie bei Parkinson".
5. **End card:** the CTA pill "Erstgespräch anfragen", plus selmazuhause.de and the logo (white on navy, or royal on mint).

### Rules
- Keep body text in videos at least 40 px and on screen for at least 3 s per line.
- Add subtitles to every video.
- Use slow reveals only (see Motion), with no fast cuts or flashing.

---

## 13. Quick checklist

- [ ] Atkinson Hyperlegible Next, body ≥ 18 px (≥ 40 px in video)
- [ ] Navy headings, ink body, teal-strong only for actions and small accents
- [ ] Bright teal `#0e9399` used only for decoration, never for text
- [ ] At least one signature motif (peach dashes, highlighter, offset block, number circles)
- [ ] Everything rounded (22/28 px), soft navy-tinted shadow
- [ ] Contrast ≥ 4.5:1 for all text
- [ ] German, "Sie", concrete, calm; facts match the website
- [ ] Reduced-motion version / subtitles for moving pieces
