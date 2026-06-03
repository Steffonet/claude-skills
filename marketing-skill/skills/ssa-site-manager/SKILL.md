---
name: "ssa-site-manager"
description: "Personal skill for managing smartsolutionappliances.com — Stan's appliance repair WordPress site. Use when working on the SSA site: aicom MCP API operations, service area page rewrites, Rank Math SEO, plugin management, Avada theme. Triggers: 'SSA site', 'smartsolutionappliances', 'service area page', 'WP-CLI', 'fix Russian Hill', 'rewrite service area', 'aicom MCP', 'batch update'. Personal skill — not for upstream contribution."
license: MIT
metadata:
  version: 2.0.0
  author: Stan Varashilov (Steffonet)
  category: marketing
  personal: true
  updated: 2026-06-03
---

# SSA Site Manager

You are managing **smartsolutionappliances.com** — Stan's WordPress appliance repair site for Smart Solution Appliances in San Francisco.

**Primary method:** aicom MCP HTTP API (no PHP scripts needed — call directly via curl).  
**Fallback:** SSH + WP-CLI (for plugin management, DB operations MCP can't do).

---

## Connection Details

```
SSH:     ssh -p 65002 u167650519@195.35.10.12
WP path: /home/u167650519/domains/smartsolutionappliances.com/public_html
WP-CLI:  wp --path=/home/u167650519/domains/smartsolutionappliances.com/public_html --allow-root
DB:      host=127.0.0.1 | user=u167650519_rNGZ9 | db=u167650519_5eTv0
```

**aicom MCP API:**
```
Endpoint: https://smartsolutionappliances.com/wp-json/aicom/v1/mcp
Key:      aicom_489622bd_bc270646f2a5fedd4b26f88298ca80e22e32157b
Auth:     Authorization: Bearer <key>
```

> Note: aicom uses HTTP JSON-RPC transport (not SSE). Call via curl directly — mcp-remote does not work with this endpoint.

---

## aicom MCP — How to Call

```bash
KEY="aicom_489622bd_bc270646f2a5fedd4b26f88298ca80e22e32157b"
EP="https://smartsolutionappliances.com/wp-json/aicom/v1/mcp"

mcp() {
  curl -s -X POST "$EP" \
    -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d "$1"
}
```

### Session workflow (required for any write operation)

```bash
# 1. Open session (REQUIRED before any write)
mcp '{"jsonrpc":"2.0","method":"session.open","params":{"name":"Service area rewrite — Lower Haight","description":"Updating post content and Rank Math meta for ID 3099"},"id":1}'

# 2. Do your work (see below)

# 3. Close session
mcp '{"jsonrpc":"2.0","method":"session.close","params":{},"id":99}'
```

Read-only tools (no session needed): `wp.posts.get`, `wp.posts.list`, `wp.meta.get`, `wp.plugins.list`, etc.

---

## Service Area Rewrite — MCP Workflow

This replaces the old PHP script + SCP deployment pattern. Call MCP directly.

```bash
POST_ID=3099
CONTENT='<!-- wp:paragraph --><p>Content here...</p><!-- /wp:paragraph -->'
RM_TITLE='Appliance Repair in Lower Haight, SF | Smart Solution Appliances'
RM_DESC='Same-day appliance repair in Lower Haight SF. Call (415) 728-4163.'
RM_KW='appliance repair lower haight'

# Backup first
mcp "{\"jsonrpc\":\"2.0\",\"method\":\"backup.post.create\",\"params\":{\"post_id\":$POST_ID},\"id\":2}"

# Update content
mcp "{\"jsonrpc\":\"2.0\",\"method\":\"wp.posts.update\",\"params\":{\"id\":$POST_ID,\"post_content\":\"$CONTENT\",\"post_status\":\"publish\"},\"id\":3}"

# Set Rank Math meta (all 3 in one call)
mcp "{\"jsonrpc\":\"2.0\",\"method\":\"wp.meta.set_many\",\"params\":{\"post_id\":$POST_ID,\"meta\":{\"rank_math_title\":\"$RM_TITLE\",\"rank_math_description\":\"$RM_DESC\",\"rank_math_focus_keyword\":\"$RM_KW\"}},\"id\":4}"
```

> For long content with special characters, write a Bash script that base64-encodes the JSON payload rather than inlining it — avoids shell escaping issues.

### Page rewrite checklist
- [ ] 1000+ words minimum
- [ ] Neighborhood-specific opening (landmarks, housing type, character)
- [ ] 3+ appliance types mentioned naturally
- [ ] Rank Math: focus keyword, meta title, meta description set
- [ ] Internal links to 2+ nearby service area pages
- [ ] FAQ section (3–5 neighborhood-relevant questions)
- [ ] CTA with phone: (415) 728-4163
- [ ] Backup created before update

---

## Critical Bugs (open)

### 1. Russian Hill broken slug (ID 3116)
Slug is doubled: `russian-hill-94109russian-hill-94109` → 404. Fix via MCP:
```bash
mcp '{"jsonrpc":"2.0","method":"wp.posts.update","params":{"id":3116,"post_name":"russian-hill-94109"},"id":1}'
```

### 2. Focus keywords — 75 pages missing
Fix via WP-CLI (MCP can't do bulk SQL):
```bash
wp --path=... --allow-root db query "
UPDATE wp_postmeta pm
JOIN wp_posts p ON pm.post_id = p.ID
SET pm.meta_value = CONCAT(REPLACE(REPLACE(LOWER(p.post_title),' (', ' '),')',''), ' appliance repair')
WHERE pm.meta_key = 'rank_math_focus_keyword'
  AND pm.meta_value = ''
  AND p.post_type = 'service_areas';"
```

---

## Service Area Rewrite Progress

**28/77 done as of 2026-06-03**

| Batch | Pages | Status |
|---|---|---|
| 1+2 | Daly City, etc. (13 pages) | Done |
| 3 | Glen Park, Hayes Valley, North Beach, Potrero Hill, Twin Peaks, Outer Sunset ×2, Alamo Square, Ashbury Heights (9) | Done |
| 5 | Lower Haight, W Addition, Fillmore, Japantown, Buena Vista, Cole Valley, Panhandle (7) | Done |
| 6 next | Tenderloin (3122), SoMa (3118), Mission Bay (3102), Dogpatch (3082), South Beach (3117), Bayview (3071), Civic Center (3076) | TODO |

Remaining after batch 6: Presidio Heights, Presidio, Sea Cliff, Lake Street, Central Richmond, and Bay Area suburbs (Brisbane, Pacifica, SSF, Sausalito, Oakland, etc.)

---

## Plugin Stack — Full Audit (43 active, 2026-06-03)

### Keep — Essential

| Plugin | Version | Role |
|---|---|---|
| Avada Builder (fusion-builder) | 3.15.4 | Page builder — core Avada component |
| Avada Core (fusion-core) | 5.15.4 | Core Avada component — required |
| Advanced Custom Fields | 6.8.3 | Custom fields (check if Avada or CPT uses it) |
| Custom Post Type UI | 1.19.2 | Registers `service_areas` CPT |
| Rank Math SEO | 1.0.271.1 | SEO titles, meta, schema |
| Rank Math SEO PRO | 3.0.114 | Pro SEO features |
| LiteSpeed Cache | 7.8.1 | Full-page caching + CDN + WebP |
| AICOM - AI Commander | 3.8.3 | MCP endpoint for Claude |
| AI Provider for Anthropic | 1.0.3 | Claude API integration |
| WP Mail SMTP | 4.8.0 | Transactional email |
| WP Consent API | 2.0.1 | GDPR consent framework |
| Website LLMs.txt | 8.4.0 | llms.txt for AI crawlers |
| SVG Support | 2.5.16 | SVG uploads |
| Jobber | 1.0.0 | Job management integration — keep if in use |
| Leaflet Map | 3.4.6 | Map embeds — keep if maps on site |

### Deactivate — Safe

| Plugin | Reason |
|---|---|
| **WooCommerce** | Services-only site, 0 products |
| **WooPayments** | WooCommerce dependency |
| **WooCommerce Shipping** | WooCommerce dependency |
| **WooCommerce Square** | WooCommerce dependency |
| **WooCommerce PayPal Payments** | WooCommerce dependency |
| **WooCommerce Analytics** | WooCommerce dependency |
| **WooCommerce Legacy REST API** | WooCommerce dependency |
| **WooCommerce.com Update Manager** | WooCommerce dependency |
| **Google for WooCommerce** | WooCommerce dependency |
| **LitCommerce** | WooCommerce dependency |
| Rocket Lazy Load | Redundant — LiteSpeed Cache handles lazy loading |
| Hostinger AI Assistant | Replaced by Claude |
| The Events Calendar | Services site — no events |
| Avada Custom Branding | White-label — not needed on own site |
| Hostinger Reach | Promotional — low value |
| InstaWP Connect | Staging tool — deactivate on production |
| WP Mail Logging | Debug-only, not needed on production |

### Review — Justify Use

| Plugin | Question |
|---|---|
| Jetpack | Heavy (5MB+). What specific feature is in use? CDN? Stats? |
| MailPoet | Active campaigns? Or replaced by Klaviyo? |
| Klaviyo | Active email list? |
| Kliken Ads + Pixel for Meta | Active ad spend? |
| Google Site Kit | GA4 already via direct tag in wp-config? |
| Hostinger Tools | Any feature in active use? |
| AI (ai 1.0.1) | What is this? Different from AICOM? |

### Deactivate WooCommerce via WP-CLI
```bash
wp --path=/home/u167650519/domains/smartsolutionappliances.com/public_html --allow-root \
  plugin deactivate woocommerce woocommerce-payments woocommerce-shipping woocommerce-square \
  woocommerce-paypal-payments woocommerce-analytics woocommerce-legacy-rest-api woo-update-manager \
  google-listings-and-ads litcommerce rocket-lazy-load hostinger-ai-assistant the-events-calendar \
  instawp-connect wp-mail-logging fusion-white-label-branding
```

> Always `wp db export` first. Deactivating WooCommerce alone frees 15–40MB/request.

---

## Rank Math SEO — Per-Page Fields

| Field | Value |
|---|---|
| Focus keyword | `[neighborhood] appliance repair` |
| Meta title | `Appliance Repair in [Neighborhood], SF | Smart Solution Appliances` |
| Meta description | `[Specific hook]. Same-day service, $95 diagnostic fee, 90-day warranty. Call (415) 728-4163.` (140–155 chars) |
| Robots | Index, Follow |
| Schema | LocalBusiness (auto via mu-plugin) |

Set via MCP `wp.meta.set_many` — no wp-admin clicking needed.

---

## DB Backup

```bash
# Via WP-CLI before any bulk operation
wp --path=... --allow-root db export ~/.dbdumps/wp_backup_$(date +%Y%m%d_%H%M).sql

# Via MCP for individual posts (before content edits)
mcp '{"jsonrpc":"2.0","method":"backup.post.create","params":{"post_id":3099},"id":1}'
```

---

## Key Numbers

| What | Value |
|---|---|
| Phone | (415) 728-4163 |
| License | BHGS #48896 |
| Review count | 134+ |
| Diagnostic fee | $95 (credited to repair) |
| Warranty | 90-day parts & labor |
| Theme | Avada 7.15.4 |

---

## Related Skills

- **avada-site-manager** — Avada theme specifics: Theme Options, Fusion Builder, CSS overrides
- **wordpress-site-manager** — Generic WP operations and health checks
- **local-seo-manager** — GBP audit, NAP consistency, schema markup
- **gbp-content-creator** — GBP posts and Q&A generation
