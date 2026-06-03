---
name: "avada-site-manager"
description: "Avada WordPress theme management for smartsolutionappliances.com. Use when working with Avada 7.15.4: Theme Options navigation, Fusion Builder vs Block Editor decisions, service_areas CPT template editing, CSS overrides, Avada performance settings, plugin conflicts. Triggers: 'Avada', 'Fusion Builder', 'Theme Options', 'Avada layout', 'CSS override', 'page template', 'Avada performance', 'Avada header', 'service area template'. Pairs with ssa-site-manager and wordpress-site-manager."
license: MIT
metadata:
  version: 1.0.0
  author: Stan Varashilov (Steffonet)
  category: marketing
  personal: true
  updated: 2026-06-03
---

# Avada Site Manager

You are working with **Avada 7.15.4** on **smartsolutionappliances.com** — an appliance repair WordPress site in San Francisco.

Avada requires two plugins: **Avada Core** (5.15.4) and **Avada Builder** (3.15.4). Both must stay active. The theme files live at `wp-content/themes/Avada/`.

---

## Avada Admin Menu Map

```
WP Admin sidebar:
└── Avada
    ├── Dashboard         — License, support, updates
    ├── Theme Options     — Global settings (colors, fonts, layout, header, footer)
    ├── Elements          — Global elements (reusable content blocks)
    ├── Studio            — Pre-built layout import
    ├── Typography        — Global font stack
    ├── Sliders           — Revolution Slider / Avada Slider management
    ├── Forms             — Avada Forms builder
    ├── Icons             — Custom icon sets
    └── Patcher           — Emergency bug patches from Avada
```

---

## Theme Options — Key Sections

Navigate via: **Avada → Theme Options**

| Section | What to find there |
|---|---|
| **Layout** | Site width, boxed vs wide, sidebar defaults |
| **Header** | Header layout (sticky, transparent), logo settings, top bar |
| **Footer** | Footer columns, colors, widget areas |
| **Colors** | Primary accent color, body text, background |
| **Typography** | Global font families and sizes (override per-page is possible) |
| **Menu** | Nav menu styling, mobile menu breakpoint |
| **Sidebar** | Global sidebar position for pages/posts |
| **Blog** | Blog archive layout (not relevant for SSA — no blog) |
| **Portfolio** | Portfolio layout settings |
| **Social Media** | Social icon links shown in header/footer |
| **Custom CSS** | ⚠️ Do NOT use this — see CSS Override section below |
| **Performance** | Minification, lazy load, Google Fonts optimization |
| **SEO** | Avada's built-in SEO — DISABLE — Rank Math handles all SEO |
| **Advanced** | Dynamic CSS, Google Maps API key, code injection fields |

---

## CSS Override — Where to Write Custom CSS

**Correct location: Appearance → Customize → Additional CSS** (bottom of panel)  
Or: **Avada → Theme Options → Advanced → CSS Code Field**

**Do NOT edit:**
- `wp-content/themes/Avada/style.css` — overwritten on theme updates
- `wp-content/themes/Avada/custom.css` — wiped on updates
- Child theme CSS (`Avada-child/style.css`) — fine if child theme is active, but Avada child theme is not installed on this site

**Safe pattern for persistent overrides:**
```css
/* In Appearance → Customize → Additional CSS */
/* [Description of what this does and why] */
.service-area-hero { padding-top: 60px; }
```

**Current known overrides (2026-06-03):**
- SHOP NOW floating button suppressed via mu-plugin `suppress-mcp-adapter-errors.php` (not CSS)

---

## Fusion Builder vs Block Editor — Decision Guide

Avada supports both editors. On this site, content editing uses different tools depending on context:

| What you're editing | Use |
|---|---|
| Service area page **layout** (header, hero, sections) | Avada Fusion Builder |
| Service area page **text content** | Block Editor (Gutenberg) or Backend Editor |
| Homepage, about page, landing pages | Avada Fusion Builder |
| Blog posts (if any) | Block Editor |
| Avada global elements (headers, footers) | Fusion Builder |

**Service area pages use Gutenberg block format** for content (`<!-- wp:paragraph -->` etc.). This is important: when updating service area content via MCP `wp.posts.update`, the content must be Gutenberg block markup — NOT Fusion Builder shortcodes.

### How to tell which editor a page uses
In wp-admin → Pages/Posts → Edit: if you see the Avada Builder blue bar at the top, it's using Fusion Builder. If you see the standard Gutenberg block editor, it's using Block Editor. Service area pages should show Gutenberg.

### Avada Builder warning
**Never save a service area page in Avada Fusion Builder** unless you intend to convert it. Avada Builder wraps the content in `[fusion_builder_container]` shortcodes, which will strip or break the existing Gutenberg block markup.

---

## Editing Service Areas CPT — Safe Workflow

The `service_areas` custom post type uses Gutenberg blocks for content.

### Safe edit flow (via MCP):
1. Open a session: `session.open`
2. Backup the post: `backup.post.create`
3. Update content: `wp.posts.update` with Gutenberg block HTML
4. Set Rank Math meta: `wp.meta.set_many`
5. Verify preview: `wp.posts.preview_url` → open in browser
6. Close session: `session.close`

### Safe edit flow (via wp-admin):
1. Go to service_areas → Edit
2. Use **Backend Editor** (not Avada Builder)
3. Make changes in the Gutenberg block editor
4. Save — do NOT click "Edit with Avada Builder"

### Template for service_areas
The shared template is accessed via: **WP Admin → Avada → Elements** or **Pages → Templates**.  
Service area pages inherit the default page template. The page-level layout (header image, breadcrumbs) is controlled by Avada's page options in the sidebar when editing.

---

## Avada Page-Level Options

When editing any page, the Avada meta box appears below the editor. Key settings:

| Setting | What it controls |
|---|---|
| **Page Template** | Full Width, Default, Blank (no header/footer) |
| **Sidebar** | Show/hide and position |
| **Page Title Bar** | Show/hide the breadcrumb/title header |
| **Featured Image** | Use as hero image |
| **Footer** | Show/hide site footer |
| **Padding** | Override global page padding |

For service area pages: Page Title Bar should be ON (shows neighborhood name as h1). Full Width template keeps content readable.

---

## Avada Performance Settings

Access via: **Avada → Theme Options → Performance**

| Setting | Recommended | Note |
|---|---|---|
| Dynamic CSS | External file | Reduces inline `<style>` bloat |
| JS Compiler | Combined + Minified | Be careful — test for breaks |
| Google Fonts | Combine into one request | Reduces HTTP requests |
| Lazy Load Images | ON | LiteSpeed Cache also does this — leave BOTH on |
| Defer JS | OFF initially | Avada Fusion Builder scripts may break with defer |

**Avada + LiteSpeed Cache — avoid conflicts:**
- Do NOT enable LiteSpeed's "Minify CSS" if Avada's CSS Compiler is on — double minification can break layouts
- LiteSpeed CDN handles static assets — Avada's own CDN setting should be OFF
- LiteSpeed Object Cache is fine alongside Avada

**After any Avada Theme Options save:** Clear LiteSpeed Cache:
```bash
wp --path=... --allow-root litespeed-purge purge_all
```
Or: WP Admin → LiteSpeed Cache → Toolbox → Purge All

---

## Avada Header Configuration

Access via: **Avada → Theme Options → Header**

Current known issue: A "SHOP NOW" floating button was appearing from a WooCommerce/Avada integration. **Fixed via mu-plugin** (`/wp-content/mu-plugins/suppress-mcp-adapter-errors.php`). Do not remove that mu-plugin.

Header types available in Avada 7.15.4:
- Header v1–v7 (preset layouts)
- Custom header (build in Avada Builder)

For SSA: Using a standard preset header with the phone number and navigation.

---

## Avada Sliders

Access via: **Avada → Sliders** (uses LayerSlider or Revolution Slider if installed, otherwise Avada Slider).

SSA site may have sliders on the homepage. **Do not delete sliders** — check if they're in use first:
```bash
# Find posts/pages referencing a slider
wp --path=... --allow-root post meta search --meta_key=_avada_slider
```

---

## Avada Global Elements (Reusable Content)

Access via: **Avada → Elements**

These are globally reusable content blocks inserted with `[fusion_global id="XXX"]` shortcode. If you change a global element, it changes everywhere it's used.

Before editing a global element:
1. Search for where it's used: WP Admin → Elements → "Used In" column
2. Backup the element data
3. Preview changes before saving

---

## Common Avada Operations

### Check which version is installed
```bash
wp --path=... --allow-root theme get Avada --field=version
# Also check child theme
wp --path=... --allow-root theme list
```

### Export Theme Options backup
WP Admin → Avada → Theme Options → Import/Export → Export Current Settings. Download the JSON. Do this before any major Theme Options changes.

### Flush Avada dynamic CSS
Avada generates a `fusion-styles.css` file dynamically. If styles seem stale after a Theme Options change:
WP Admin → Avada → Dashboard → click "Regenerate CSS"

Or via WP-CLI:
```bash
wp --path=... --allow-root option delete fusion_dynamic_css_ids
wp --path=... --allow-root litespeed-purge purge_all
```

### Update Avada safely
1. Export Theme Options first (backup JSON)
2. DB backup: `wp db export`
3. WP Admin → Avada → Dashboard → check for updates
4. Update Avada Theme, then Avada Core, then Avada Builder (in that order)
5. Clear all caches after update

---

## Plugin Conflicts to Watch

| Plugin combination | Issue | Fix |
|---|---|---|
| Avada Builder + Block Editor | Fusion Builder wraps overwrite Gutenberg blocks | Use Backend Editor for service area pages |
| Rank Math + Avada SEO | Schema conflicts, duplicate meta tags | Avada SEO must be DISABLED in Theme Options → SEO |
| LiteSpeed Cache + Avada CSS Compiler | Double minification breaks layouts | Disable one; LiteSpeed CSS minify OFF is safer |
| WooCommerce + Avada | Floating SHOP NOW button | Fixed via mu-plugin |
| Jetpack + Avada CDN | CDN URL conflicts | If using both, disable one CDN |

### Verify Avada SEO is disabled
```bash
wp --path=... --allow-root option get fusion_options | grep -i seo
```
Should show SEO fields as empty or "0". If Rank Math AND Avada SEO both generate `<title>` tags, Google sees duplicate titles.

---

## Avada Studio — Use Carefully

Avada → Studio contains pre-built layouts you can import. **Do not import Studio layouts onto existing service area pages** — they will overwrite the Gutenberg block content with Fusion Builder shortcodes and break the SEO content structure.

Studio is safe for: creating new pages from scratch, homepage sections, landing pages.

---

## Reference Files

- [Avada Theme Options Reference](references/avada-theme-options.md) — section-by-section settings guide
- [Fusion Builder Block Reference](references/fusion-builder-blocks.md) — common element types and their params

---

## Related Skills

- **ssa-site-manager** — MCP API operations, service area rewrites, plugin management
- **wordpress-site-manager** — Generic WP health checks, WP-CLI patterns, DB cleanup
- **local-seo-manager** — GBP, schema, NAP consistency
