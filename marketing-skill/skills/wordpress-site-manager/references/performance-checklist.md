# WordPress Performance Checklist — 50 Points

Use alongside the `wordpress-site-manager` skill for full performance audits. Run `scripts/wp_audit_runner.py --sections perf` to generate the audit commands.

---

## 1. Caching — 10 Points

- [ ] A caching plugin is active (LiteSpeed Cache, WP Rocket, W3 Total Cache — only ONE)
- [ ] Page caching enabled (HTML pages cached to disk or memory)
- [ ] Browser caching headers configured (Cache-Control, Expires)
- [ ] Object caching enabled (Redis or Memcached — check with hosting provider)
- [ ] Database query caching via object cache
- [ ] Full-page cache bypass rules set correctly (WooCommerce cart, checkout, account pages)
- [ ] CDN configured for static assets (images, CSS, JS) if traffic > 10k visits/month
- [ ] Cache warming configured (pre-generates cache after purge)
- [ ] Cache exclusions set for logged-in users and dynamic pages
- [ ] Cache purge triggered automatically on post update/publish

---

## 2. Images — 8 Points

- [ ] Images compressed before upload (TinyPNG, Squoosh, or plugin-based)
- [ ] WebP format enabled and served (LiteSpeed Cache → Media → Generate WebP)
- [ ] Lazy loading enabled for below-the-fold images
- [ ] Images served at correct dimensions (no oversized images scaled down in HTML)
- [ ] Maximum upload size set (large uncompressed images cause slow uploads + bloat)
- [ ] Featured images optimized (homepage/archive page — these load first)
- [ ] Unused image sizes registered by themes/plugins removed (reduces DB bloat)
- [ ] Logo and favicon files appropriately sized (logo ≤ 50KB; favicon ≤ 10KB)

---

## 3. CSS / JS Optimization — 8 Points

- [ ] CSS minification enabled
- [ ] JS minification enabled
- [ ] JS defer enabled (test for breakage — Avada/Elementor may need exclusions)
- [ ] Render-blocking CSS removed or deferred (Google PageSpeed will flag this)
- [ ] Unused CSS removed or purged (LiteSpeed CSS Combine + Remove Unused CSS)
- [ ] Third-party scripts loaded asynchronously (analytics, chat widgets, ad pixels)
- [ ] No unused plugins loading scripts on every page (plugin_auditor.py finds these)
- [ ] Google Fonts loaded locally or preconnected (eliminates external DNS lookup)

---

## 4. Database — 10 Points

- [ ] Autoloaded options < 300KB
  ```sql
  SELECT ROUND(SUM(LENGTH(option_value))/1024) AS autoload_kb FROM wp_options WHERE autoload='yes'
  ```
- [ ] No orphaned plugin data in wp_options (check for deactivated plugin name prefixes)
- [ ] Transients cleaned (expired transients deleted)
- [ ] Post revisions limited (`WP_POST_REVISIONS = 5` in wp-config.php)
- [ ] Spam and trash comments deleted
- [ ] Trashed posts deleted
- [ ] Database tables optimized (`wp db optimize`)
- [ ] wp_postmeta not bloated by abandoned plugin data
- [ ] Action Scheduler table not oversized (WooCommerce + Jetpack write heavily here)
- [ ] wp_actionscheduler_logs cleaned if > 50k rows

---

## 5. Server & Hosting — 8 Points

- [ ] PHP version ≥ 8.1 (8.3 preferred — significant performance gains over 7.x)
- [ ] OPcache enabled (PHP bytecode cache — huge impact; hosting control panel)
- [ ] Memory limit adequate: `WP_MEMORY_LIMIT = '256M'` minimum
- [ ] Max execution time: 60-120 seconds (prevents timeout on large operations)
- [ ] GZIP / Brotli compression enabled for text responses (hosting panel or .htaccess)
- [ ] HTTPS everywhere with HTTP/2 (HTTP/2 enables request multiplexing)
- [ ] Server-side image processing (ImageMagick preferred over GD)
- [ ] Cron runs via real server cron, not WP-Cron (set `DISABLE_WP_CRON = true` + crontab)

---

## 6. WordPress Configuration — 6 Points

- [ ] `WP_POST_REVISIONS` set in wp-config.php (default is unlimited — bloats database)
- [ ] `AUTOSAVE_INTERVAL` set (default 60 seconds is aggressive for large post editors)
- [ ] `WP_DEBUG` off on production (`define('WP_DEBUG', false)`)
- [ ] Heartbeat API rate limited or disabled on front-end (reduces admin-ajax.php load)
  ```php
  add_filter('heartbeat_settings', function($settings) {
      $settings['interval'] = 60; // seconds (default: 15)
      return $settings;
  });
  ```
- [ ] Emoji scripts disabled if not using emojis in content
  ```php
  remove_action('wp_head', 'print_emoji_detection_script', 7);
  remove_action('wp_print_styles', 'print_emoji_styles');
  ```
- [ ] XML-RPC disabled if not needed (Jetpack may need it — check before disabling)

---

## Quick Wins (Highest ROI, Lowest Effort)

These 5 items fix the most performance issues per hour of effort:

1. **Autoload cleanup** — 30 minutes, eliminates DB overhead on every page load
2. **Delete post revisions** — 5 minutes, frees disk space and speeds backup
3. **Enable LiteSpeed WebP** — 10 minutes, typically 30-50% image size reduction
4. **Enable JS defer** — 5 minutes, usually removes render-blocking resources warning
5. **Upgrade PHP to 8.3** — hosting panel change, 10-20% throughput improvement

---

## Scoring

- 45-50 checks: Production-optimized — focus on content and growth
- 35-44 checks: Good baseline with gaps — prioritize caching and database
- 20-34 checks: Meaningful improvements available — start with Quick Wins
- Under 20: Performance bottlenecks likely affecting rankings and conversion
