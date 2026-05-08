# Frontend Stock, Localization, And Dark Lake Plan

Goal: clean up the storefront presentation by removing visible stock counts, rewriting Russian copy so it no longer reads like a literal English translation, and shifting the visual design toward a darker Baikal lake aesthetic with blue/dark-blue product cards.

## Current Situation

- Product card layout was previously improved using a premium forest/lake direction.
- The current CSS is already dark green/lake-inspired, but the next pass should move further away from green dominance and toward a dark lake/blue mood.
- Product detail still exposes exact stock count.
- Cart quantity controls still need stock limits internally, but the storefront does not need to show inventory numbers.
- Russian localization exists in `app/i18n.py` and product seed text, but it should be reviewed as Russian copy, not as translated English.

## Design Direction

Use the successful frontend requirements from `codex_tasks/completed_tasks/codex_plans_log.md` as the baseline:

- robust product card structure
- fixed image containers
- no overlap between images and text/actions
- product metadata below image
- footer row with price and Add button
- dense but readable product grid
- restrained premium catalog feel
- responsive 4/2/1 column behavior
- polished hover states

Change the aesthetic from forest green to dark Baikal lake:

- Background: very deep lake blue / near-black blue
  - examples: `#07141d`, `#091923`, `#0b1d2a`
- Section background: cold deep-water blue
  - examples: `#0f2634`, `#123044`
- Product card background: blue or dark blue, not white
  - examples: `#102b3d`, `#12354a`, `#0f2a3a`
- Product image frame background: darker blue with subtle cool contrast
  - examples: `#0a1f2d`, `#18384c`
- Primary text: pale ice / lake foam
  - examples: `#eef7fb`, `#e3f0f5`
- Secondary text: misty blue-gray
  - examples: `#a8bdc8`, `#90a8b5`
- Accent: clear Baikal blue / cyan-blue
  - examples: `#6bb7d6`, `#75c6e8`
- CTA: strong lake blue or icy teal
  - examples: `#3f9ec4`, `#4ab3d8`
- CTA hover: brighter cold blue
  - examples: `#74c9e8`, `#8ad8f2`
- Border: muted steel-blue
  - examples: `#25475a`, `#31586d`

Avoid:

- beige/cream/sand dominance
- brown/orange/espresso dominance
- purple/purple-blue gradients
- one-note green palette
- decorative orbs/blobs
- nested cards

## Remove Visible Stock Counts

Remove exact stock count from customer-facing UI.

Required changes:

- Remove stock row from product detail page.
- Remove or stop using `t("stock")` in visible templates unless an operator/admin view later needs it.
- Product cards should not show stock count.
- Cart page may keep numeric input `max` internally, but should not display phrases like "only X available".
- Validation errors should explain that the requested quantity is unavailable without exposing exact inventory counts.

Keep backend stock logic:

- Cart quantity must still be capped by stock.
- Checkout must still reject insufficient stock.
- YooKassa/fake payment reservation logic must still protect inventory.
- Tests should verify the UI no longer renders exact stock on product detail/catalog/cart validation while backend limits still work.

## Russian Localization Rewrite

Read every Russian customer-facing string with this premise:

> This currently sounds like a neural-machine translation of the English site. Rewrite it as natural Russian copy with similar meaning, appropriate for a small premium Baikal stone storefront.

Files/areas to review:

- `app/i18n.py`
- `app/seed.py` Russian product names
- `app/seed.py` Russian product descriptions
- `app/templates/*.html` if any hardcoded Russian text exists
- validation messages
- checkout/order/tracking/payment texts
- color labels
- order status/payment status labels
- outbound Telegram notification text if it becomes customer/operator visible in this pass

Copy rules:

- Russian should be natural and idiomatic, not word-for-word English.
- Keep meaning close to the original business intent.
- Keep tone calm, grounded, and premium.
- Do not invent mystical, medical, investment, or unsupported properties.
- Product descriptions should talk about color, texture, shape, origin, and decorative use.
- Keep labels short where the UI is compact.
- Avoid bureaucratic or overly formal phrases unless they fit checkout/legal context.
- Ensure button text fits on mobile.

Examples of direction:

- Instead of literal "семейство цвета", use "оттенок" or "цветовая группа" depending on context.
- Instead of clumsy translated hero copy, write a native Russian sentence about selected Baikal stones for interior/decor.
- Instead of "данные доставки" everywhere, consider where "доставка" or "адрес доставки" is enough.

## Product Card And Layout Requirements

Preserve the previous successful card structure:

- image area on top
- metadata row below image
- title
- short description
- footer row with price and Add button

Specific requirements:

- Product cards must have a dark blue/blue background.
- Text must stay readable against card background.
- Product image frames must not overlap text.
- Product image frame should use fixed aspect ratio.
- Cards should keep consistent heights.
- Hover image scale must stay inside image frame.
- No text should sit on top of product images except a small intentional badge.
- Price and Add button must stay aligned on desktop and not overflow on mobile.
- Product grid remains responsive:
  - desktop: 4 columns where space allows
  - tablet: 2 columns
  - mobile: 1 column

## Page-Level Frontend Requirements

Review:

- header/navigation
- hero/catalog intro
- filter tabs
- product cards
- product detail page
- cart drawer/page
- checkout page
- order success/tracking pages

Required outcomes:

- The first screen still feels like a usable store, not a marketing landing page.
- The dark lake palette feels cohesive but not one-note.
- Blue/dark-blue product cards stand out from the page background.
- Links/buttons have clear hover/focus states.
- Form inputs are readable in dark mode.
- Error messages remain visible and accessible.
- No text overflows buttons, cards, or mobile containers.

## Tests And Verification

Add or update tests:

- Russian i18n keys still exist for all templates.
- Product detail page no longer displays exact stock label/count.
- Catalog/product cards do not display stock count.
- Stock validation errors do not reveal exact available quantity.
- Cart/backend stock validation still works.
- Checkout still rejects insufficient stock.
- Existing localized product names/descriptions render.

Manual/browser verification:

- Run app locally.
- Use Playwright screenshots or browser checks for:
  - desktop catalog
  - mobile catalog
  - product detail
  - cart
  - checkout
  - tracking page
- Confirm no product image overlaps title/description/price/button.
- Confirm product cards are dark blue/blue, not white.
- Confirm Russian text reads naturally in key customer paths.

Recommended commands:

```bash
uv run pytest
uv run pytest tests/e2e
uv run pytest --cov=app
```

## Implementation Order

1. Audit templates for visible stock output.
2. Remove exact stock count from product/customer UI while preserving backend limits.
3. Replace exact-stock validation copy such as `only_available` with non-enumerating availability copy.
4. Audit all Russian strings in `app/i18n.py`.
5. Rewrite Russian UI strings naturally.
6. Audit Russian product names/descriptions in `app/seed.py`.
7. Rewrite product Russian copy where it sounds translated or awkward.
8. Update CSS variables toward dark lake blue palette.
9. Make product cards blue/dark-blue and verify contrast.
10. Recheck product card layout against the prior successful card requirements.
11. Add/update tests for stock visibility and localization coverage.
12. Run tests and browser/layout verification.

## Acceptance Criteria

- Customer-facing UI no longer shows exact stock counts.
- Customer-facing validation does not reveal exact stock counts.
- Backend stock caps, checkout validation, and payment reservation behavior still work.
- Russian customer-facing copy reads naturally and no longer feels like literal English translation.
- Product cards use blue/dark-blue backgrounds.
- Overall site palette reads as dark Baikal lake, not green/forest or beige/brown.
- Product images never overlap text/actions.
- Mobile and desktop layouts remain polished and readable.
- Tests pass, including E2E tests.
