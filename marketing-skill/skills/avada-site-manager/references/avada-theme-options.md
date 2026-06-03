# Avada Theme Options — Section Reference

Avada 7.15.4 | Path: WP Admin → Avada → Theme Options

## Layout
- Site Width: max-width of the site container (default 1170px)
- Site Layout: Wide (full-width) or Boxed
- Sidebar Sizes: default widths for sidebar/content split

## Header
- Header Layout: v1–v7 preset, or Custom
- Sticky Header: scroll behavior
- Header Background: color or image
- Logo: image path, width, retina version
- Top Bar: phone/email strip above main header
- Tagline: show/hide site tagline in header

## Menu
- Main Menu font size, weight, hover effect
- Dropdown style (flyout vs mega menu)
- Mobile menu breakpoint (px)
- "Back" button in mobile menu

## Footer
- Footer Columns: 1–6 columns, each a widget area
- Footer Background color
- Copyright bar text
- Social icons in footer: on/off

## Colors
- Primary Color: accent/CTA color (buttons, links, highlights)
- Secondary Color: used for secondary buttons, highlights
- Body Background: site background
- Content Background: content area background

## Typography
- Body font: family, size, weight, line-height
- Heading fonts (H1–H6): can set separately
- Menu font
- All can be overridden per-page via Page Options

## Performance (important for SSA)
- Dynamic CSS Method: Inline (default) or External File (recommended)
- JS Compiler: None, Combined, Combined + Minified
- Google Fonts: separate requests or combined
- Lazy Load: CSS background images
- Preload Critical Images: specify paths

## SEO ⚠️
**Must be DISABLED on SSA.** Rank Math handles all SEO.
- Disable: "Add Open Graph Meta Tags" → OFF
- Disable: "Add Twitter Card Meta Tags" → OFF
- Disable: "Add Schema Markup" → OFF (Rank Math + mu-plugin handle schema)

## Advanced
- Google Maps API Key: needed for any map embeds
- Custom CSS: use this field OR Appearance → Customize → Additional CSS (not both)
- Code injection: `<head>`, before `</body>` fields for scripts
- Override Post Types: which CPTs Avada controls
- Smooth Scrolling: js-based smooth scroll

## Import/Export
Export current settings as JSON before major changes.
Import path: same panel → Import tab → paste JSON.
