---
name: "ssa-site-manager"
description: "Personal skill for managing smartsolutionappliances.com — Stan's appliance repair WordPress site in San Francisco. Use when working on the SSA site: SSH operations, WP-CLI commands, service area page rewrites, Rank Math SEO, Avada theme fixes, plugin management. Triggers: 'SSA site', 'smartsolutionappliances', 'service area page', 'WP-CLI', 'fix Russian Hill', 'rewrite service area'. This is a personal skill — not intended for upstream contribution."
license: MIT
metadata:
  version: 1.0.0
  author: Stan Varashilov (Steffonet)
  category: marketing
  personal: true
  updated: 2026-06-03
---

# SSA Site Manager

You are managing **smartsolutionappliances.com** — Stan's WordPress appliance repair site for Smart Solution Appliances in San Francisco.

This skill contains all shortcuts, commands, and context for operating this site. Always read `ssa-context.md` if it exists in the project before starting.

---

## Server Access

```
SSH:     ssh -p 65002 u167650519@195.35.10.12
WP path: /home/u167650519/domains/smartsolutionappliances.com/public_html
WP-CLI:  wp --path=/home/u167650519/domains/smartsolutionappliances.com/public_html --allow-root
DB host: 127.0.0.1 | user: u167650519_rNGZ9 | db: u167650519_5eTv0
```

**WordPress MCP:** `https://smartsolutionappliances.com/wp-json/easy-mcp-ai/v1/mcp/wpmcp_53411d9addcef5cd98303a08db0629ea8cfc1d54073cbe12b0558af3113f17f9`

---

## Critical Bugs (fix before any other work)

### 1. Russian Hill broken slug (ID 3116)
Current slug is doubled (`russian-hill-94109russian-hill-94109`) — causes 404:
```bash
wp --path=/home/u167650519/domains/smartsolutionappliances.com/public_html --allow-root \
  post update 3116 --post_name="russian-hill-94109"
```

### 2. Focus keywords — 75 pages missing
75 of 77 service_areas pages have no Rank Math focus keyword set. Bulk fix:
```sql
-- Run via: wp --allow-root db query < fix-keywords.sql
UPDATE wp_postmeta pm
JOIN wp_posts p ON pm.post_id = p.ID
SET pm.meta_value = CONCAT(
  REPLACE(REPLACE(LOWER(p.post_title), ' (', ' '), ')', ''),
  ' appliance repair'
)
WHERE pm.meta_key = 'rank_math_focus_keyword'
  AND pm.meta_value = ''
  AND p.post_type = 'service_areas';
```

### 3. Deactivate dead plugins
```bash
wp --path=... --allow-root plugin deactivate woocommerce woocommerce-payments wc-order-status-manager
```

---

## Service Area Pages — Rewrite Workflow

**The problem:** 75 of 77 pages are 400-word identical templates. Google marks them as thin/duplicate doorway content → not indexed.

**Gold standard:** Daly City (ID 3954) — rewritten 2026-05-30, 1000+ words, fully unique. Use as the template.

**Priority rewrite order** (highest SF traffic neighborhoods first):
1. Richmond District (94121)
2. Mission District (94110)
3. Pacific Heights (94115)
4. Sunset District (94122)
5. Castro (94114)
6. Fix Russian Hill slug → then rewrite it
7. Resolve Outer Sunset duplicate (IDs 3940 + 3109)

### Page rewrite checklist
- [ ] 1000+ words minimum
- [ ] Neighborhood-specific opening paragraph (landmarks, character, typical housing)
- [ ] Primary service + 3 appliance types mentioned naturally
- [ ] Rank Math focus keyword set: `[neighborhood] appliance repair`
- [ ] Meta description 140–155 chars including neighborhood + phone
- [ ] LocalBusiness schema auto-added by mu-plugin (verify areaServed)
- [ ] Internal link to at least 2 other service area pages
- [ ] FAQ section (3–5 questions, neighborhood-relevant)
- [ ] CTA with phone: (415) 728-4163

---

## Rank Math SEO — Service Area Page Settings

Access: WP Admin → Rank Math → Posts → service_areas

Per-page required fields:
| Field | Value |
|---|---|
| Focus keyword | `[neighborhood] appliance repair` |
| Meta title | `Appliance Repair in [Neighborhood], SF | Smart Solution Appliances` |
| Meta description | `Fast appliance repair in [Neighborhood], San Francisco. Washer, dryer, fridge, dishwasher, oven. Same-day service. Call (415) 728-4163.` |
| Robots | Index, Follow |
| Schema | LocalBusiness (auto via mu-plugin) |

Bulk-set focus keywords via WP-CLI:
```bash
wp --path=... --allow-root post meta update POST_ID rank_math_focus_keyword "richmond appliance repair"
```

---

## Avada Theme — Known Issues & Fixes

**Global Header bug (FIXED):** SHOP NOW floating button was showing — suppressed in mu-plugin `suppress-mcp-adapter-errors.php`.

**Service area page template:** Posts use the `service_areas` custom post type. Edit via Avada Builder → Templates → service_areas.

**Page builder tip:** When editing a service area page in Avada, use "Backend Editor" not the visual builder — the visual builder can accidentally strip Rank Math meta.

**CSS override location:** Appearance → Custom CSS (bottom of file). Don't edit Avada child theme CSS — it gets wiped on updates.

---

## Plugins — Keep / Deactivate Reference

**Active (keep):**
- Rank Math Pro — SEO (needs license renewal in wp-admin)
- LiteSpeed Cache — performance
- Wordfence — security
- WP Mail SMTP — transactional email
- Easy MCP AI — WordPress MCP endpoint
- Enhanced Local Schema (mu-plugin, custom)

**Deactivate (safe to remove):**
- WooCommerce + all WC plugins (0 products, not in use)
- Broken Link Checker (hammers DB on every crawl)
- Google Analytics Dashboard for WP (replaced by GA4 direct tag)

---

## DB Backup

```bash
# Quick backup before any bulk changes
wp --path=... --allow-root db export ~/.dbdumps/wp_backup_$(date +%Y%m%d).sql
```

Existing backup: `~/.dbdumps/wp_backup_pre_update.sql` (455MB, taken 2026-05-30)

---

## GBP Weekly Posts

Automated via Postiz. Schedule rotates 4 topics by ISO week mod 4.
- Postiz API Key in memory: `project_smartsolution_seo.md`
- To check current week's topic: `python3 -c "import datetime; w=datetime.date.today().isocalendar()[1]; topics=['tips','promo','review_ask','seasonal']; print(topics[w%4])"`

---

## What Remains (as of 2026-06-03)

| Task | Status |
|---|---|
| Fix Russian Hill slug (ID 3116) | NOT DONE |
| Bulk fix 75 focus keywords | NOT DONE |
| Deactivate dead plugins | NOT DONE |
| Validate Search Console fix | Stan to click manually |
| Rewrite 76 service area pages | IN PROGRESS (1/77 done — Daly City) |
| Fix NAP on Yelp, BBB, Angi | NOT DONE |
| Authenticate Ahrefs for keyword gap | NOT DONE |
