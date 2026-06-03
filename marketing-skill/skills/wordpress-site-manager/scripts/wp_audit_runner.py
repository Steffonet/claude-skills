#!/usr/bin/env python3
"""
wp_audit_runner.py — WordPress audit shell script generator.

Takes your site config (SSH, WP path) and generates a ready-to-run shell script
of WP-CLI audit commands. Paste or pipe the output to your terminal.

Usage:
    python3 wp_audit_runner.py [--config config.json] [--sections all|health|plugins|perf|security]
    python3 wp_audit_runner.py  (runs with sample config for demo)

Config JSON format:
    {
        "wp_path": "/home/u123456/domains/example.com/public_html",
        "wp_cli": "/usr/local/bin/wp",
        "allow_root": true,
        "ssh": "ssh -p 65002 user@host"
    }

Output: Shell script with all audit commands, formatted for easy review.
"""

import json
import sys
import argparse
from typing import Dict, List


def build_wp_cmd(config: Dict) -> str:
    cli = config.get("wp_cli", "wp")
    path = config.get("wp_path", "")
    root = "--allow-root" if config.get("allow_root", False) else ""
    parts = [cli]
    if path:
        parts.append(f"--path={path}")
    if root:
        parts.append(root)
    return " ".join(parts)


def section_health(wp: str) -> List[str]:
    return [
        "# ═══════════════════════════════════════════",
        "# HEALTH CHECK",
        "# ═══════════════════════════════════════════",
        "",
        "echo '--- Core integrity ---'",
        f"{wp} core verify-checksums",
        "",
        "echo '--- Active plugins ---'",
        f"{wp} plugin list --status=active --fields=name,version,auto_update,update --format=table",
        "",
        "echo '--- Autoload size (target: < 300KB) ---'",
        f"""{wp} db query "SELECT ROUND(SUM(LENGTH(option_value))/1024) AS autoload_kb FROM wp_options WHERE autoload='yes'"  """,
        "",
        "echo '--- Top 20 autoloaded options ---'",
        f"""{wp} db query "SELECT option_name, ROUND(LENGTH(option_value)/1024,1) AS kb FROM wp_options WHERE autoload='yes' ORDER BY kb DESC LIMIT 20"  """,
        "",
        "echo '--- Transient count ---'",
        f"""{wp} db query "SELECT COUNT(*) AS transient_count FROM wp_options WHERE option_name LIKE '_transient_%'"  """,
        "",
        "echo '--- Database table sizes ---'",
        f"{wp} db size --tables",
        "",
        "echo '--- Cron health ---'",
        f"{wp} cron test",
        f"{wp} cron event list --fields=hook,next_run_relative,schedule | head -20",
        "",
        "echo '--- PHP version ---'",
        "php -v | head -1",
        "",
    ]


def section_plugins(wp: str) -> List[str]:
    return [
        "# ═══════════════════════════════════════════",
        "# PLUGIN AUDIT",
        "# ═══════════════════════════════════════════",
        "",
        "echo '--- Exporting plugin list for auditor ---'",
        f"{wp} plugin list --status=active --format=json > active-plugins.json",
        "echo 'Saved to active-plugins.json'",
        "echo 'Run: python3 scripts/plugin_auditor.py --plugins active-plugins.json'",
        "",
        "echo '--- Plugins with pending updates ---'",
        f"{wp} plugin list --update=available --format=table",
        "",
        "echo '--- Plugins with auto-update OFF ---'",
        f"{wp} plugin list --status=active --auto_update=off --fields=name,version --format=table",
        "",
        "echo '--- Check for default admin username ---'",
        f"""{wp} user list --role=administrator --fields=ID,user_login,user_email --format=table  """,
        "",
    ]


def section_performance(wp: str) -> List[str]:
    return [
        "# ═══════════════════════════════════════════",
        "# PERFORMANCE",
        "# ═══════════════════════════════════════════",
        "",
        "echo '--- Autoload detail by prefix ---'",
        f"""{wp} db query "SELECT SUBSTRING_INDEX(option_name,'_',2) AS prefix, COUNT(*) AS count, ROUND(SUM(LENGTH(option_value))/1024,1) AS total_kb FROM wp_options WHERE autoload='yes' GROUP BY prefix ORDER BY total_kb DESC LIMIT 20"  """,
        "",
        "echo '--- Post revision count ---'",
        f"""{wp} db query "SELECT COUNT(*) AS revision_count FROM wp_posts WHERE post_type='revision'"  """,
        "",
        "echo '--- Draft/trash post count ---'",
        f"""{wp} db query "SELECT post_status, COUNT(*) AS count FROM wp_posts WHERE post_type='post' GROUP BY post_status"  """,
        "",
        "echo '--- Spam/trash comment count ---'",
        f"""{wp} db query "SELECT comment_approved, COUNT(*) AS count FROM wp_comments GROUP BY comment_approved"  """,
        "",
        "echo '--- WooCommerce product count (0 = safe to deactivate WC) ---'",
        f"""{wp} post list --post_type=product --post_status=publish --format=count 2>/dev/null || echo 'WooCommerce not active'  """,
        "",
        "echo '--- Large wp_options rows (any autoload setting) ---'",
        f"""{wp} db query "SELECT option_name, autoload, ROUND(LENGTH(option_value)/1024,1) AS kb FROM wp_options ORDER BY kb DESC LIMIT 10"  """,
        "",
    ]


def section_security(wp: str) -> List[str]:
    return [
        "# ═══════════════════════════════════════════",
        "# SECURITY",
        "# ═══════════════════════════════════════════",
        "",
        "echo '--- wp-config.php permissions ---'",
        "stat -c '%a %n' wp-config.php 2>/dev/null || stat -f '%p %N' wp-config.php",
        "echo '(Should be 600)'",
        "",
        "echo '--- Check DISALLOW_FILE_EDIT in wp-config ---'",
        "grep -i 'disallow_file' wp-config.php && echo 'FOUND' || echo 'MISSING — add: define(DISALLOW_FILE_EDIT, true)'",
        "",
        "echo '--- Check WP_DEBUG status ---'",
        "grep -i 'wp_debug' wp-config.php",
        "",
        "echo '--- Admin users ---'",
        f"{wp} user list --role=administrator --fields=ID,user_login,user_email,registered --format=table",
        "",
        "echo '--- Check for default admin username ---'",
        f"""{wp} user get admin --field=user_login 2>/dev/null && echo '⚠  WARNING: Rename admin user' || echo 'OK — no default admin username'  """,
        "",
        "echo '--- Inactive users (no login in 365 days) ---'",
        f"""{wp} db query "SELECT user_login, user_email, user_registered FROM wp_users WHERE user_login NOT IN (SELECT user_login FROM wp_users u JOIN wp_usermeta m ON u.ID=m.user_id WHERE meta_key='session_tokens') LIMIT 10"  """,
        "",
        "echo '--- mu-plugins list ---'",
        f"{wp} plugin list --status=must-use --fields=name,version --format=table",
        "",
        "echo '--- Core update status ---'",
        f"{wp} core check-update",
        "",
    ]


def build_script(config: Dict, sections: List[str]) -> str:
    wp = build_wp_cmd(config)
    ssh = config.get("ssh", "")

    header = [
        "#!/bin/bash",
        "# WordPress Audit Script",
        f"# Generated by wp_audit_runner.py",
        f"# WP path: {config.get('wp_path', '')}",
        "",
    ]
    if ssh:
        header += [
            f"# SSH connection: {ssh}",
            f"# Run this script on the server via SSH, or prefix each command with:",
            f"# {ssh} 'COMMAND'",
            "",
        ]
    header += [
        "set -e",
        f"WP='{wp}'",
        "",
        "# Quick sanity check",
        f"$WP --version || {{ echo 'WP-CLI not found at {config.get(\"wp_cli\", \"wp\")}'; exit 1; }}",
        "",
    ]

    body = []
    section_map = {
        "health":   section_health,
        "plugins":  section_plugins,
        "perf":     section_performance,
        "security": section_security,
    }

    run_sections = sections if sections != ["all"] else list(section_map.keys())
    for s in run_sections:
        fn = section_map.get(s)
        if fn:
            body.extend(fn(wp))

    footer = [
        "",
        "# ═══════════════════════════════════════════",
        "echo ''",
        "echo 'Audit complete. Review output above for issues.'",
        "echo 'Run plugin_auditor.py against active-plugins.json for plugin recommendations.'",
    ]

    return "\n".join(header + body + footer)


# ─── Sample config ────────────────────────────────────────────────────────────

SAMPLE_CONFIG = {
    "wp_path": "/home/u167650519/domains/smartsolutionappliances.com/public_html",
    "wp_cli": "wp",
    "allow_root": True,
    "ssh": "ssh -p 65002 u167650519@195.35.10.12",
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WordPress audit shell script generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", help="Path to site config JSON")
    parser.add_argument(
        "--sections",
        nargs="+",
        choices=["all", "health", "plugins", "perf", "security"],
        default=["all"],
        help="Which sections to include (default: all)",
    )
    parser.add_argument("--output", help="Save script to file instead of stdout")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = SAMPLE_CONFIG
        print("# [INFO] No --config provided. Using sample config.\n", file=sys.stderr)

    script = build_script(config, args.sections)

    if args.output:
        with open(args.output, "w") as f:
            f.write(script)
        print(f"Script saved to {args.output}")
        print(f"Make it executable: chmod +x {args.output}")
    else:
        print(script)


if __name__ == "__main__":
    main()
