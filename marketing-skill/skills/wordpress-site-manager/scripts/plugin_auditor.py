#!/usr/bin/env python3
"""
plugin_auditor.py — WordPress plugin categorization tool.

Takes `wp plugin list --format=json` output and categorizes each plugin as:
  KEEP        — core functionality, no viable replacement
  DEACTIVATE  — redundant, unused, or confirmed dead weight
  REVIEW      — heavy/complex plugin that needs a justification check

Usage:
    # Generate input:
    wp plugin list --status=active --format=json > active-plugins.json

    # Run:
    python3 plugin_auditor.py --plugins active-plugins.json
    python3 plugin_auditor.py --plugins active-plugins.json --output markdown

If no input file is provided, runs with embedded sample data for demonstration.

Output: Plugin audit table with recommendation and reason.
"""

import json
import sys
import argparse
from typing import Dict, List, Tuple


# ─── Categorization rules ─────────────────────────────────────────────────────
# Each entry: (slug_pattern, category, reason)
# Patterns are substring matches against plugin slug (lowercased).
# First match wins — order matters.

RULES: List[Tuple[str, str, str]] = [
    # ── Page builders / themes ──────────────────────────────────────────────
    ("fusion-builder",          "KEEP",       "Avada page builder — required if using Avada theme"),
    ("fusion-core",             "KEEP",       "Avada core — required if using Avada theme"),
    ("fusion-white-label",      "DEACTIVATE", "White-label branding — decorative, zero value on live site"),
    ("elementor",               "KEEP",       "Page builder — required if using Elementor layouts"),
    ("divi",                    "KEEP",       "Divi builder — required if using Divi theme"),

    # ── SEO ─────────────────────────────────────────────────────────────────
    ("rank-math",               "KEEP",       "SEO plugin — primary SEO (Rank Math)"),
    ("seo-by-rank-math",        "KEEP",       "SEO plugin — primary SEO (Rank Math)"),
    ("yoast",                   "REVIEW",     "SEO plugin — conflicts with Rank Math if both active; use one SEO plugin only"),
    ("wordpress-seo",           "REVIEW",     "Yoast SEO — conflicts with Rank Math if both active"),
    ("aioseo",                  "REVIEW",     "All-in-One SEO — conflicts with Rank Math if both active"),

    # ── Caching ─────────────────────────────────────────────────────────────
    ("litespeed",               "KEEP",       "Caching — LiteSpeed server-level cache + optimization"),
    ("w3-total-cache",          "REVIEW",     "Caching — redundant if LiteSpeed Cache active; use one caching plugin"),
    ("wp-super-cache",          "REVIEW",     "Caching — redundant if LiteSpeed Cache active; use one caching plugin"),
    ("wp-rocket",               "REVIEW",     "Caching — redundant if LiteSpeed Cache active; use one caching plugin"),
    ("autoptimize",             "REVIEW",     "Optimization — redundant if LiteSpeed Cache handles minification"),

    # ── Performance / CDN ───────────────────────────────────────────────────
    ("rocket-lazy-load",        "DEACTIVATE", "Lazy load — redundant; LiteSpeed Cache includes lazy loading"),
    ("smush",                   "REVIEW",     "Image optimization — verify LiteSpeed WebP doesn't overlap"),
    ("imagify",                 "REVIEW",     "Image optimization — verify LiteSpeed WebP doesn't overlap"),

    # ── Security ────────────────────────────────────────────────────────────
    ("wordfence",               "KEEP",       "Security — firewall + malware scanner"),
    ("sucuri",                  "KEEP",       "Security — WAF + monitoring"),
    ("ithemes-security",        "KEEP",       "Security — hardening plugin"),
    ("really-simple-ssl",       "KEEP",       "SSL — forces HTTPS (can be replaced with wp-config.php line)"),

    # ── Forms ───────────────────────────────────────────────────────────────
    ("wpforms",                 "KEEP",       "Forms — contact/lead forms"),
    ("gravityforms",            "KEEP",       "Forms — advanced forms"),
    ("contact-form-7",          "REVIEW",     "Forms — if WPForms is active, this is likely redundant"),
    ("ninja-forms",             "REVIEW",     "Forms — if WPForms is active, this is likely redundant"),

    # ── E-commerce ──────────────────────────────────────────────────────────
    ("woocommerce",             "REVIEW",     "E-commerce — heavy platform; justify if site has 0 active products"),
    ("woo-update-manager",      "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-payments",    "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-square",      "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-paypal",      "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-shipping",    "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-analytics",   "REVIEW",     "WooCommerce addon — deactivate with WooCommerce if shop unused"),
    ("woocommerce-legacy",      "REVIEW",     "WooCommerce legacy API — deactivate if shop unused"),
    ("litcommerce",             "REVIEW",     "Multi-channel selling — justify if selling on eBay/Amazon"),

    # ── Email marketing ─────────────────────────────────────────────────────
    ("mailpoet",                "REVIEW",     "Email marketing — justify: is there an active subscriber list?"),
    ("klaviyo",                 "REVIEW",     "Email/SMS marketing — redundant if MailPoet active; use one"),
    ("mailchimp",               "REVIEW",     "Email marketing — justify: is there an active subscriber list?"),

    # ── Analytics / Ads ─────────────────────────────────────────────────────
    ("google-site-kit",         "KEEP",       "Analytics — Google Analytics + Search Console bridge"),
    ("google-listings",         "REVIEW",     "Google Shopping — justify: is there an active product feed?"),
    ("kliken",                  "REVIEW",     "Meta pixel / ads — justify: are Meta ads actively running?"),
    ("meta-pixel",              "REVIEW",     "Meta pixel — justify: are Meta ads actively running?"),

    # ── Maps ────────────────────────────────────────────────────────────────
    ("leaflet-map",             "REVIEW",     "Maps — verify: is it embedded on any live page?"),

    # ── Booking / CRM ───────────────────────────────────────────────────────
    ("jobber",                  "KEEP",       "Booking/CRM — core business system integration"),

    # ── Backup ──────────────────────────────────────────────────────────────
    ("updraftplus",             "KEEP",       "Backup — primary backup solution"),
    ("duplicator",              "REVIEW",     "Backup/migration — if UpdraftPlus active, this is redundant"),

    # ── Custom fields ───────────────────────────────────────────────────────
    ("advanced-custom-fields",  "KEEP",       "Custom fields — ACF; keep if theme/CPTs depend on it"),
    ("custom-post-type-ui",     "KEEP",       "Custom post types — CPT UI; keep if CPTs are registered here"),

    # ── Email deliverability ─────────────────────────────────────────────────
    ("wp-mail-smtp",            "KEEP",       "Email delivery — routes WordPress email through SMTP"),
    ("wp-mail-logging",         "KEEP",       "Email logging — useful for debugging delivery issues"),

    # ── Jetpack ─────────────────────────────────────────────────────────────
    ("jetpack",                 "REVIEW",     "Jetpack — heavy plugin; audit which modules are actually used"),

    # ── Hosting integrations ─────────────────────────────────────────────────
    ("hostinger",               "KEEP",       "Hosting integration — system plugin, leave alone"),
    ("hostinger-ai-assistant",  "DEACTIVATE", "Hostinger AI chat — unnecessary with Claude"),
    ("hostinger-reach",         "DEACTIVATE", "Hostinger marketing upsell — no value"),
    ("hostinger-auto-updates",  "KEEP",       "Hosting system plugin — leave alone"),
    ("hostinger-preview",       "KEEP",       "Hosting system plugin — leave alone"),

    # ── Consent / GDPR ──────────────────────────────────────────────────────
    ("wp-consent",              "KEEP",       "Consent API — GDPR compliance layer"),
    ("cookieyes",               "KEEP",       "Cookie consent — GDPR compliance"),

    # ── SVG / media ─────────────────────────────────────────────────────────
    ("svg-support",             "KEEP",       "SVG support — needed if theme uses SVG logos/icons"),

    # ── Events ──────────────────────────────────────────────────────────────
    ("the-events-calendar",     "DEACTIVATE", "Events calendar — no events on a service business; almost certainly unused"),
    ("tribe-events",            "DEACTIVATE", "Events — unused on service business"),

    # ── Misc utilities ──────────────────────────────────────────────────────
    ("query-monitor",           "REVIEW",     "Dev tool — should be deactivated on production"),
    ("debug-bar",               "REVIEW",     "Dev tool — should be deactivated on production"),
    ("wp-crontrol",             "REVIEW",     "Cron tool — dev/debug tool; deactivate when not investigating cron"),
    ("redirection",             "KEEP",       "Redirects — manages 301/302 redirects"),
    ("classic-editor",          "REVIEW",     "Classic editor — verify if any content requires it; block editor preferred"),
    ("website-llms-txt",        "KEEP",       "AI crawler — generates llms.txt for AI search visibility"),
]

CATEGORY_ORDER = {"DEACTIVATE": 0, "REVIEW": 1, "KEEP": 2}
CATEGORY_LABELS = {
    "KEEP":       "✅ Keep",
    "DEACTIVATE": "❌ Deactivate",
    "REVIEW":     "⚠️  Review",
}


def categorize_plugin(slug: str) -> Tuple[str, str]:
    slug_lower = slug.lower()
    for pattern, category, reason in RULES:
        if pattern in slug_lower:
            return category, reason
    return "REVIEW", "No rule matched — manually verify this plugin's purpose and value"


def audit_plugins(plugins: List[Dict]) -> List[Dict]:
    results = []
    for plugin in plugins:
        slug = plugin.get("name", plugin.get("slug", "unknown"))
        version = plugin.get("version", "")
        auto_update = plugin.get("auto_update", "")
        update = plugin.get("update", "none")
        category, reason = categorize_plugin(slug)
        results.append({
            "slug": slug,
            "version": version,
            "auto_update": auto_update,
            "update": update,
            "category": category,
            "reason": reason,
        })
    results.sort(key=lambda x: (CATEGORY_ORDER[x["category"]], x["slug"]))
    return results


def format_markdown(results: List[Dict]) -> str:
    lines = []
    current_category = None
    counts = {"KEEP": 0, "DEACTIVATE": 0, "REVIEW": 0}
    for r in results:
        counts[r["category"]] += 1

    lines.append("# WordPress Plugin Audit")
    lines.append("")
    lines.append(f"**Total active:** {len(results)}  |  "
                 f"✅ Keep: {counts['KEEP']}  |  "
                 f"❌ Deactivate: {counts['DEACTIVATE']}  |  "
                 f"⚠️  Review: {counts['REVIEW']}")
    lines.append("")

    for r in results:
        if r["category"] != current_category:
            current_category = r["category"]
            lines.append(f"## {CATEGORY_LABELS[current_category]}")
            lines.append("")
            lines.append("| Plugin | Version | Update | Reason |")
            lines.append("|---|---|---|---|")

        update_flag = "🔄 Available" if r["update"] not in ("none", "", None) else "—"
        lines.append(f"| `{r['slug']}` | {r['version']} | {update_flag} | {r['reason']} |")

    lines.append("")
    if counts["DEACTIVATE"] > 0:
        deactivate_slugs = [r["slug"] for r in results if r["category"] == "DEACTIVATE"]
        lines.append("## Deactivate Command")
        lines.append("")
        lines.append("```bash")
        lines.append("wp plugin deactivate " + " ".join(deactivate_slugs))
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("*Audit rules are heuristic. Verify REVIEW items before deactivating.*")

    return "\n".join(lines)


def format_table(results: List[Dict]) -> str:
    col_widths = {
        "slug": max(len(r["slug"]) for r in results) + 2,
        "category": 12,
        "reason": 60,
    }
    header = (
        f"{'Plugin':<{col_widths['slug']}} "
        f"{'Status':<{col_widths['category']}} "
        f"Reason"
    )
    divider = "-" * (col_widths["slug"] + col_widths["category"] + 65)
    lines = ["", "WordPress Plugin Audit", "=" * len("WordPress Plugin Audit"), "",
             header, divider]
    for r in results:
        lines.append(
            f"{r['slug']:<{col_widths['slug']}} "
            f"{r['category']:<{col_widths['category']}} "
            f"{r['reason']}"
        )
    lines.append(divider)
    lines.append(f"Total: {len(results)} | "
                 f"Keep: {sum(1 for r in results if r['category']=='KEEP')} | "
                 f"Deactivate: {sum(1 for r in results if r['category']=='DEACTIVATE')} | "
                 f"Review: {sum(1 for r in results if r['category']=='REVIEW')}")
    return "\n".join(lines)


# ─── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_PLUGINS = [
    {"name": "fusion-builder", "version": "3.15.3", "auto_update": "on", "update": "none"},
    {"name": "fusion-core", "version": "5.15.3", "auto_update": "on", "update": "none"},
    {"name": "fusion-white-label-branding", "version": "2.0.3", "auto_update": "on", "update": "none"},
    {"name": "seo-by-rank-math", "version": "1.0.271", "auto_update": "on", "update": "none"},
    {"name": "seo-by-rank-math-pro", "version": "3.0.114", "auto_update": "off", "update": "available"},
    {"name": "litespeed-cache", "version": "7.8.1", "auto_update": "on", "update": "none"},
    {"name": "rocket-lazy-load", "version": "2.3.9", "auto_update": "off", "update": "none"},
    {"name": "advanced-custom-fields", "version": "6.8.2", "auto_update": "off", "update": "none"},
    {"name": "custom-post-type-ui", "version": "1.19.2", "auto_update": "on", "update": "none"},
    {"name": "wpforms-lite", "version": "1.10.1", "auto_update": "off", "update": "none"},
    {"name": "wp-mail-smtp", "version": "4.8.0", "auto_update": "off", "update": "none"},
    {"name": "woocommerce", "version": "9.8.5", "auto_update": "off", "update": "none"},
    {"name": "woocommerce-payments", "version": "9.7.2", "auto_update": "on", "update": "none"},
    {"name": "woocommerce-square", "version": "4.9.0", "auto_update": "on", "update": "none"},
    {"name": "woocommerce-analytics", "version": "1.5.2", "auto_update": "off", "update": "none"},
    {"name": "the-events-calendar", "version": "6.9.3", "auto_update": "on", "update": "available"},
    {"name": "jetpack", "version": "15.8", "auto_update": "on", "update": "none"},
    {"name": "google-site-kit", "version": "1.179.0", "auto_update": "on", "update": "none"},
    {"name": "hostinger", "version": "3.0.66", "auto_update": "on", "update": "none"},
    {"name": "hostinger-ai-assistant", "version": "1.2.0", "auto_update": "off", "update": "none"},
    {"name": "jobber", "version": "1.0.0", "auto_update": "on", "update": "none"},
    {"name": "mailpoet", "version": "5.9.1", "auto_update": "on", "update": "none"},
    {"name": "klaviyo", "version": "3.4.0", "auto_update": "on", "update": "none"},
]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WordPress plugin auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--plugins", help="Path to wp plugin list --format=json output")
    parser.add_argument("--output", choices=["markdown", "table"], default="markdown",
                        help="Output format (default: markdown)")
    args = parser.parse_args()

    if args.plugins:
        with open(args.plugins) as f:
            plugins = json.load(f)
    else:
        plugins = SAMPLE_PLUGINS
        print("[INFO] No --plugins file provided. Using sample data.\n")

    results = audit_plugins(plugins)

    if args.output == "markdown":
        print(format_markdown(results))
    else:
        print(format_table(results))


if __name__ == "__main__":
    main()
