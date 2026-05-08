# Frontend Hero And Card Color Refactor

Goal: simplify the catalog hero and make product cards fit the dark lake visual direction. Remove the hero stats block entirely, reduce the hero height roughly by half, and adjust stone card colors so cards are clearly blue/dark-blue and distinct from the page background.

## Current Situation

- `app/templates/index.html` renders `.store-hero` with two children:
  - `.hero-copy`
  - `.hero-stats`
- `.hero-stats` shows the product count and `stones_available` text.
- `static/styles.css` makes `.store-hero` a two-column grid with large vertical padding:
  - top padding up to `122px`
  - bottom padding up to `72px`
- `.hero-stats` has its own large card style.
- Hero text is still visually constrained by `.hero-copy { max-width: 780px; }`, global `h1 { max-width: 15ch; }`, and `.hero-copy p:not(.eyebrow) { max-width: 62ch; }`.
- `.stone-card` uses `--color-card: #102f43`; if the card still reads beige/washed out in the browser, the product card surface and image-frame colors need to move cooler and more clearly blue.

## Desired Result

- The hero becomes a compact intro band, not a large landing-style section.
- The `.hero-stats` div is removed from the template.
- The hero height is approximately two times smaller than the current version.
- The hero text spans the available content width instead of sitting as a narrow block in the left corner.
- The hero headline and supporting copy both participate in the full-width hero layout; do not leave the headline capped at `15ch`.
- The hero remains readable and visually intentional on desktop and mobile.
- Product cards use a clearly blue/dark-blue surface that is distinct from:
  - `--color-background`
  - `--color-section`
  - image frame background
- No beige/cream/sand-looking card surfaces remain in the selling item UI.

## Implementation Details

Template changes:

- Edit `app/templates/index.html`.
- Remove:

```html
<div class="hero-stats">...</div>
```

- Keep `.hero-copy`, `h1`, and hero paragraph.
- Do not remove product count logic from backend routes unless it becomes unused elsewhere; this is a frontend cleanup.

CSS changes:

- Update `.store-hero` from a two-column grid to a single-column layout or keep grid with one content column.
- Make `.hero-copy` use the full available hero content width:

```css
.hero-copy {
  width: 100%;
  max-width: none;
}
```

- Override the global hero heading constraint inside the hero:

```css
.store-hero h1 {
  max-width: none;
}
```

- Relax `.hero-copy p:not(.eyebrow)` from the current narrow `62ch`. If the paragraph becomes too long on very wide screens, use a much wider responsive cap or a balanced text layout, but do not return to a left-corner block.
- Reduce vertical padding to about half, for example:

```css
padding: clamp(34px, 5vw, 62px) clamp(18px, 5vw, 64px) clamp(24px, 4vw, 42px);
```

- Remove `.hero-stats` and `.hero-stats strong` styles if they become unused.
- Consider reducing hero `h1` max size if the compact hero feels crowded.
- Revisit these selling-item variables/selectors:
  - `--color-card`
  - `.stone-card`
  - `.stone-image-frame`
- For product cards, prefer a cooler card surface such as `#12384f`, `#12354a`, or `#0f344a`.
- Keep image frame darker than card body, for example `#081f2f` or `#0b2638`.
- Make sure card border is visible but subtle.
- Leave cart/order surfaces alone unless they are directly affected by shared CSS variables.

Do not:

- Add decorative blobs/orbs.
- Create a marketing-only hero.
- Put cards inside cards.
- Change checkout/payment/order behavior.

## Tests And Verification

Add or update tests:

- Catalog page no longer renders `hero-stats`.
- Catalog page still renders hero title/copy and product grid.
- CSS no longer contains active `.hero-stats` rules after markup removal.
- Existing catalog/E2E tests still pass.

Manual/browser verification:

- Desktop catalog: hero is visibly shorter, product grid is closer to first viewport.
- Desktop catalog: hero text uses the available horizontal space and does not look tucked into the left corner.
- Desktop catalog: hero headline is not constrained to a narrow 15-character column.
- Mobile catalog: hero text fits without excessive vertical blank space.
- Product cards are blue/dark-blue and do not look beige or white.
- Product card text, price, and button remain readable.
- Images still stay inside their frame and never overlap text/actions.

Recommended commands:

```bash
uv run pytest
uv run pytest tests/e2e
uv run pytest --cov=app
```

## Implementation Order

1. Remove `.hero-stats` markup from `app/templates/index.html`.
2. Simplify `.store-hero` layout and reduce vertical padding.
3. Expand `.hero-copy`, `.store-hero h1`, and hero paragraph layout so the hero text spans the available content width.
4. Remove unused `.hero-stats` CSS.
5. Adjust product card and image-frame colors toward cool blue/dark-blue.
6. Add or update catalog test for removed hero stats.
7. Run tests and verify desktop/mobile catalog visually.

## Acceptance Criteria

- No `.hero-stats` div is rendered.
- No active `.hero-stats` CSS remains.
- Hero section is roughly half the current height.
- Hero headline and supporting text span the main hero width and are not visually stuck in the left corner.
- Product cards are distinctly blue/dark-blue, not beige/white.
- Product cards remain visually distinct from the page background.
- Product image/card layout remains stable on desktop and mobile.
- Tests and E2E pass.
