# WordPress Security Checklist — 40 Points

Use alongside the `wordpress-site-manager` skill for full security audits. Run `scripts/wp_audit_runner.py --sections security` to generate the audit commands.

---

## 1. wp-config.php — 8 Points

- [ ] `DISALLOW_FILE_EDIT` = true (blocks theme/plugin editor in wp-admin)
- [ ] `WP_DEBUG` = false on production (never expose errors to visitors)
- [ ] `WP_DEBUG_LOG` = false on production
- [ ] `FORCE_SSL_ADMIN` = true (forces HTTPS for wp-admin)
- [ ] File permissions: **600** (owner read/write only, not readable by web server)
  ```bash
  chmod 600 wp-config.php
  stat -c '%a %n' wp-config.php  # Should output: 600
  ```
- [ ] Database credentials are not reused elsewhere
- [ ] Secret keys and salts are unique (generate at: https://api.wordpress.org/secret-key/1.1/salt/)
- [ ] wp-config.php is above the web root (optional — move one level up from public_html)

---

## 2. File Permissions — 5 Points

- [ ] WordPress directories: **755**
- [ ] WordPress files: **644**
- [ ] wp-config.php: **600**
- [ ] uploads directory: **755** (needs to be writable by web server)
- [ ] No world-writable files (permissions 777)
  ```bash
  find /path/to/wordpress -perm 777 -type f  # Should return nothing
  ```

---

## 3. Admin Users — 6 Points

- [ ] No user with login `admin` (default username = brute-force target)
  ```bash
  wp user get admin --field=user_login 2>/dev/null && echo "RENAME THIS USER"
  ```
- [ ] Minimum admin accounts (1-2 max; one per real human)
- [ ] All admin accounts use strong unique passwords (12+ chars, not reused)
- [ ] All admin accounts use unique email addresses (not shared)
- [ ] Inactive/former employee accounts removed
- [ ] Two-factor authentication enabled for admin accounts (Wordfence, Google Authenticator)

---

## 4. Updates — 5 Points

- [ ] WordPress core is current version
- [ ] All active plugins are current version
- [ ] Active theme is current version
- [ ] PHP is current supported version (≥ 8.1)
- [ ] Auto-updates configured appropriately (core minor updates: ON; major: test first)

---

## 5. Login Hardening — 5 Points

- [ ] Login page brute-force protection active (Wordfence, Limit Login Attempts, or hosting WAF)
- [ ] XML-RPC disabled if not required by Jetpack mobile app
  ```php
  // In mu-plugins:
  add_filter('xmlrpc_enabled', '__return_false');
  ```
- [ ] REST API restricted for unauthenticated users (if no public API use case)
- [ ] Login attempts logged (Wordfence or similar)
- [ ] Login URL is not `/wp-admin` (optional obscurity via WPS Hide Login plugin)

---

## 6. Plugins — 5 Points

- [ ] No abandoned plugins (last updated > 2 years ago)
- [ ] All plugins sourced from WordPress.org or reputable paid vendors (no nulled plugins)
- [ ] Deactivated plugins deleted (deactivated ≠ removed; files still scannable)
- [ ] Number of active plugins is minimal — each plugin is a potential attack surface
- [ ] No plugins with known CVEs (check: wpscan.com/plugins or patchstack.com)

---

## 7. Core Integrity — 3 Points

- [ ] WordPress core files verified against checksums (no tampering)
  ```bash
  wp core verify-checksums
  ```
- [ ] No unexpected PHP files in wp-content (especially in uploads directory)
  ```bash
  find wp-content/uploads -name "*.php" -type f  # Should return nothing
  ```
- [ ] No unexpected admin accounts added recently
  ```bash
  wp user list --role=administrator --fields=ID,user_login,user_email,registered
  ```

---

## 8. Backups — 3 Points

- [ ] Automated daily/weekly backups running (UpdraftPlus, Jetpack Backup, hosting backup)
- [ ] Backup stored off-server (S3, Google Drive, Dropbox) — not just on the same server
- [ ] Most recent backup tested/verified (a backup that can't restore is not a backup)

---

## Quick Wins (Highest ROI, Lowest Effort)

These 5 items eliminate the most common WordPress attack vectors:

1. **Add `DISALLOW_FILE_EDIT`** — one line in wp-config.php, 30 seconds
2. **Set wp-config.php to 600** — one chmod command, 10 seconds
3. **Rename default admin user** — one DB query, 2 minutes
4. **Disable XML-RPC** — one mu-plugin, 5 minutes (test Jetpack still works)
5. **Delete deactivated plugins** — `wp plugin delete [slug]`, 5 minutes per plugin

---

## Scoring

- 36-40 checks: Hardened — monitor and maintain
- 28-35 checks: Good security posture with gaps — prioritize admin + wp-config
- 18-27 checks: Vulnerable to common attacks — address immediately
- Under 18: High risk — run through checklist systematically before doing anything else
