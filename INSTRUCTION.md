# Instruction For The Coding Agent

Build a working MVP online store for literal stones collected from Lake Baikal. The store must use the existing HTMX frontend direction in this repo, Python 3.12 with Flask for the backend, `uv` for project management, and SQLite for persistence. Do not implement real acquiring/payment processing yet; create a clean payment integration plug point so acquiring can be added later without rewriting checkout.

## Project Context

- This file is in `media/`. Treat the project root as the parent directory: `..`.
- Existing frontend files live in the project root:
  - `../index.html`
  - `../styles.css`
  - `../fragments/palette-warm-natural.html`
- The current frontend is an HTMX static prototype with the color system and component feel to preserve.
- Existing stone product images live in `media/separate_samples/`.
- There are 16 photographed stone images:
  - `stone_samples_8_stone_01.png` through `stone_samples_8_stone_08.png`
  - `stone_samples2_8_stone_01.png` through `stone_samples2_8_stone_08.png`
- The images are roughly 319-340px wide and 540-542px high. Build image containers that can handle these slight dimension differences without layout shift.

## Required Stack

- Frontend: server-rendered HTML fragments enhanced with HTMX.
- Backend: Flask on Python 3.12.
- Package/runtime management: `uv`.
- Database: SQLite.
- CSS: continue from the existing `styles.css` design language.
- Do not add a SPA framework.
- Do not add a heavy frontend build step.

## First Tasks

1. Update `pyproject.toml` so the project targets Python 3.12, not Python 3.14.
2. Add Flask as a dependency through `uv`.
3. Replace the placeholder `main.py` with a real Flask app entrypoint.
4. Keep the existing visual palette, but adapt the store brand from the furniture placeholder to a Baikal stone shop.
5. Preserve HTMX usage and make product/catalog/cart interactions happen through HTMX fragments.

## MVP Product Scope

Create a complete small-store flow:

- Home/catalog page showing all stones.
- Product cards with real stone photos from `media/separate_samples/`.
- Product detail view, preferably loaded inline or navigated to normally with server-rendered HTML.
- Filters or simple category tabs using HTMX.
- Cart drawer or cart page updated through HTMX.
- Add to cart.
- Update item quantity.
- Remove item from cart.
- Checkout form.
- Order confirmation page.
- Basic admin seed data, implemented as a local seed function or CLI command.

The user should be able to start the server, browse the catalog, add stones to cart, submit checkout details, and receive an order confirmation, all without touching external services.

## Product Data

Seed 16 products, one per image in `media/separate_samples/`.

Each product should have:

- `id`
- `slug`
- `name`
- `description`
- `price_cents`
- `image_path`
- `stock`
- `weight_grams`
- `origin`
- `finish`
- `color_family`
- `is_featured`

Use a tasteful naming system appropriate for stones from Lake Baikal, for example:

- Baikal Shoreline Pebble
- Selenga Grey Stone
- Olkhon Stripe Stone
- Listvyanka Smooth Stone
- Deep Water Granite
- Mist Vein Pebble

Do not claim supernatural, medical, investment, or scientifically unsupported properties. Keep copy grounded: texture, color, shape, origin, and decorative use.

## Database Requirements

Use SQLite with a small explicit schema. Implement schema creation in code so a fresh checkout can run without manual SQL setup.

Required tables:

- `products`
- `orders`
- `order_items`

Recommended optional table:

- `cart_items`, if you choose a server-side cart.

Session-based cart is acceptable for the MVP. If using sessions, store only product ids and quantities in the session, then read product data from SQLite.

Orders must persist:

- customer name
- email
- phone, optional
- shipping address
- order status
- payment status
- total amount
- created timestamp

Order items must persist:

- order id
- product id
- product name snapshot
- unit price snapshot
- quantity

## Payment/Acquiring Plug Point

Do not connect real acquiring yet.

Create a clear payment abstraction that can later be replaced by a real acquiring provider. For the MVP, implement a fake/manual provider with this behavior:

- On checkout submit, validate cart and customer fields.
- Create the order in SQLite with `payment_status = "pending_manual"`.
- Return an order confirmation page explaining that payment is pending and will be handled manually.

Design this as replaceable code, for example:

- `payments/base.py` with a provider interface or simple protocol.
- `payments/manual.py` with `ManualPaymentProvider`.
- `create_payment(order)` returns a structured result with fields like `status`, `payment_reference`, and optional `redirect_url`.

Do not hardcode payment logic deep inside route handlers.

## Suggested File Structure

You may adjust this if the implementation stays simple and coherent, but prefer something close to:

```text
.
├── main.py
├── pyproject.toml
├── README.md
├── store.db              # generated locally; should be gitignored if git is used
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── routes.py
│   ├── seed.py
│   ├── cart.py
│   ├── payments/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── manual.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── product_detail.html
│       ├── checkout.html
│       ├── order_success.html
│       └── fragments/
│           ├── product_grid.html
│           ├── product_card.html
│           ├── cart_drawer.html
│           ├── cart_line.html
│           └── cart_badge.html
├── static/
│   └── styles.css
└── media/
    └── separate_samples/
```

If you move `styles.css` into `static/`, update all references. Keep the stone images in `media/separate_samples/` and serve them through Flask with a route or static configuration.

## Frontend Requirements

Use HTMX for progressive interactions:

- Catalog filters: `hx-get` product grid fragments.
- Add to cart: `hx-post` and update cart badge/drawer.
- Quantity changes: `hx-post` or `hx-put` and swap cart contents.
- Remove item: `hx-delete` or `hx-post` and swap cart contents.
- Checkout validation errors: return the checkout form fragment/page with inline errors.

The app must work as normal server-rendered pages even if HTMX is unavailable for the core flow. HTMX should improve the interaction, not be the only way to use the store.

Use semantic HTML:

- Real forms and buttons.
- Product images with descriptive `alt`.
- Accessible labels for checkout fields.
- Header navigation with links to catalog and cart.

## Visual Design Requirements

Use the existing warm natural palette from `styles.css`:

- background `#F7F1E8`
- text `#2B2118`
- brand/walnut `#5A3E2B`
- secondary/clay `#B9825A`
- accent/sage `#7A8450`
- section/sand `#E6D6C3`
- border/taupe `#C6B49E`
- CTA/terracotta `#A65335`

Adapt the brand to Lake Baikal stones. Suggested brand name: `Baikal Stone Market`.

The UI should feel like a real small catalog store:

- Dense but readable product grid.
- Real stone photos are prominent.
- Product cards should use fixed image frames with `object-fit: contain` or `object-fit: cover`, whichever shows the stones best.
- Avoid marketing-only hero pages. The first screen should immediately show products or a hero with visible product grid content below.
- Avoid nested cards and excessive decoration.
- Keep border radii around 8px or less.
- Use responsive layouts for mobile and desktop.

## Backend Routes

Implement routes roughly like:

- `GET /` catalog/home.
- `GET /products/<slug>` product detail.
- `GET /fragments/products` filtered product grid.
- `POST /cart/add/<product_id>` add item.
- `GET /cart` cart page or drawer.
- `GET /fragments/cart` cart fragment.
- `POST /cart/update/<product_id>` update quantity.
- `POST /cart/remove/<product_id>` remove item.
- `GET /checkout` checkout form.
- `POST /checkout` validate and create order.
- `GET /orders/<order_id>` order confirmation.
- `POST /dev/seed` only if useful locally; otherwise seed automatically on first run.

Use redirects for non-HTMX requests and fragments for HTMX requests. Detect HTMX with the `HX-Request` header.

## Validation

Validate:

- Quantity is a positive integer.
- Quantity cannot exceed stock.
- Checkout cart cannot be empty.
- Customer name is required.
- Email is required and minimally valid.
- Shipping address is required.

Show validation errors in the UI without crashing.

## Development Experience

Make the app easy to run:

- `uv sync`
- `uv run python main.py`

The Flask server should start on a local port and print the URL.

Update `README.md` with:

- stack summary
- setup commands
- run command
- seed/reset instructions
- note that acquiring is intentionally a manual/pending plug point for now

If adding generated files, keep local runtime artifacts out of git:

- `store.db`
- `*.sqlite`
- `instance/`
- `__pycache__/`
- `.venv/`

## Acceptance Criteria

The MVP is done when:

- `uv sync` succeeds.
- `uv run python main.py` starts the Flask app.
- Visiting `/` shows a styled catalog using the real stone images.
- All 16 stones are present in the seeded catalog.
- Product cards match the existing warm natural visual system.
- Add/update/remove cart interactions work with HTMX.
- The cart also remains usable through normal form submits/redirects.
- Checkout creates a persistent order in SQLite.
- The fake/manual payment provider is used and isolated behind a replaceable payment interface.
- The order confirmation page displays order number, customer email, items, total, and manual payment status.
- No real acquiring/payment provider is called.
- The README explains how to run and what remains to integrate for payments.

## Implementation Notes

- Prefer simple Flask, Jinja templates, and standard library SQLite unless a dependency is clearly justified.
- Keep business logic out of templates where practical.
- Format prices from cents consistently.
- Use integer cents for money.
- Keep route handlers small by moving cart/database helpers into modules.
- Seed data should be idempotent: running it twice should not duplicate products.
- Do not overwrite the photographed stone assets.
- Do not remove the existing prototype files unless they are intentionally replaced by the working app.
- Before finishing, run at least a smoke test by starting the app and requesting `/`.
