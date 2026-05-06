Fix the product card image layout and improve the overall visual design.

Current issue:
The stone product images are overflowing/overfitting their product card fields. The images are too large and are being cropped by the card boundaries, causing the selling item details, title, price, weight, and Add button to overlap with the image area. Product cards should feel clean, contained, and intentional.

Required image/card fixes:
1. Make every product image live inside a dedicated image container with a fixed, consistent aspect ratio.
2. Prevent images from covering or overlapping text/content.
3. Use object-fit: cover only inside the image container, not across the whole card.
4. Add overflow-hidden to the image container, not to the whole card content area.
5. Ensure the card has a clear structure:
   - image area on top
   - product metadata below
   - footer row with price and Add button
6. Keep title, description, tag, weight, price, and button fully visible at all screen sizes.
7. Use consistent image heights across product cards.
8. Add responsive behavior:
   - desktop: 4-column grid
   - tablet: 2-column grid
   - mobile: 1-column grid
9. Add enough padding and spacing so the cards do not feel cramped.
10. Make sure no text sits on top of product images unless it is a small intentional badge.

Suggested card structure:
- Card container: rounded corners, subtle border, soft shadow, clean background.
- Image wrapper: width 100%, aspect-ratio 4 / 3 or 1 / 1, border-radius on top corners, overflow hidden.
- Image: width 100%, height 100%, object-fit: cover, display block.
- Content section: padding 16–20px.
- Badge + weight row above title or near title.
- Title: readable serif or semi-bold display style.
- Description: muted text, 2–3 line clamp.
- Footer: price left, Add button right.

Frontend style direction:
Make the site feel more premium, calm, and natural. Shift the color palette away from the current beige/brown-heavy look toward a “foresty and clean lake” aesthetic.

Color scheme:
- Background: very pale lake mist / off-white with a cool tint
  Example: #F4F8F6 or #F2F7F5
- Section background: soft lake clay / light sage
  Example: #DDE8DF or #E3ECE7
- Primary text: deep forest green
  Example: #183A2E or #1F3D34
- Secondary text: muted slate-green
  Example: #5F746B
- Primary button: pine green
  Example: #2F5D50
- Button hover: deeper evergreen
  Example: #21473D
- Accent: clean lake blue
  Example: #6FA7B8 or #8BBFCC
- Badge background: moss green
  Example: #6F8557
- Border: pale reed / misty green-gray
  Example: #C8D6CF
- Card background: warm white / lake foam
  Example: #FBFCFA

Design improvements:
1. Redesign the hero section so it feels spacious and balanced.
2. The giant headline is currently cropped at the top; fix vertical spacing and ensure the full heading is visible.
3. Use a cleaner layout with more intentional whitespace.
4. Use a refined serif for large headings and a clean sans-serif for body text.
5. Make the stat card on the right more elegant with a softer shadow, rounded corners, and forest/lake colors.
6. Make the filter buttons cleaner:
   - pill-shaped
   - active state in pine green
   - inactive state white or mist green
   - subtle border
7. Make product cards feel like premium catalog items:
   - consistent card heights
   - restrained shadows
   - soft borders
   - clear hierarchy
8. Add subtle hover states:
   - card lifts slightly
   - image gently scales inside its container
   - Add button darkens
9. Keep the design calm, minimal, and natural — no loud colors or heavy shadows.

Implementation details:
Use CSS grid for the catalog layout. Use a robust product card component structure similar to:

.card {
  background: #FBFCFA;
  border: 1px solid #C8D6CF;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(24, 58, 46, 0.08);
  display: flex;
  flex-direction: column;
}

.imageWrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #DDE8DF;
}

.imageWrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 220ms ease;
}

.card:hover .imageWrap img {
  transform: scale(1.035);
}

.cardBody {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.metaRow,
.footerRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.description {
  color: #5F746B;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.footerRow {
  margin-top: auto;
}

Primary goal:
No product image should ever overlap or crop into the text/action area. The UI should look like a polished, premium stone catalog inspired by forest green, clean lake water, mist, moss, and natural stone.