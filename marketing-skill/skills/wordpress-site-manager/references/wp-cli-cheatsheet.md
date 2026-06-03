# WP-CLI Cheatsheet

Quick reference for common WP-CLI operations. All commands assume:
```bash
WP="wp --path=/path/to/wordpress --allow-root"
```

---

## Core

```bash
# Check WP version
$WP core version

# Verify core files against checksums (detects tampering)
$WP core verify-checksums

# Check for available updates
$WP core check-update

# Update WordPress core
$WP core update

# Update database after core update
$WP core update-db
```

---

## Plugins

```bash
# List all active plugins
$WP plugin list --status=active --format=table

# List all plugins with update status
$WP plugin list --fields=name,version,auto_update,update --format=table

# List plugins with available updates
$WP plugin list --update=available --format=table

# Export active plugin list as JSON (for plugin_auditor.py)
$WP plugin list --status=active --format=json > active-plugins.json

# Update a single plugin
$WP plugin update [slug]

# Update all plugins
$WP plugin update --all

# Activate / deactivate
$WP plugin activate [slug]
$WP plugin deactivate [slug]
$WP plugin deactivate [slug1] [slug2] [slug3]

# Enable/disable auto-updates for a plugin
$WP plugin auto-updates enable [slug]
$WP plugin auto-updates disable [slug]

# Delete a deactivated plugin
$WP plugin delete [slug]

# List must-use plugins
$WP plugin list --status=must-use --format=table
```

---

## Themes

```bash
# List all themes
$WP theme list --format=table

# Check for theme updates
$WP theme list --update=available --format=table

# Update all themes
$WP theme update --all

# Activate a theme
$WP theme activate [slug]
```

---

## Database

```bash
# Export full database backup
$WP db export ~/wp_backup_$(date +%Y%m%d_%H%M).sql

# Import a backup
$WP db import backup.sql

# Run a raw SQL query
$WP db query "SELECT * FROM wp_options WHERE option_name='siteurl'"

# Optimize all tables
$WP db optimize

# Repair tables
$WP db repair

# Show table sizes
$WP db size --tables

# Search and replace across all tables (URL migration, domain change)
$WP search-replace 'http://old.com' 'https://new.com' --all-tables --dry-run
$WP search-replace 'http://old.com' 'https://new.com' --all-tables
```

---

## Options (wp_options table)

```bash
# Get an option value
$WP option get siteurl
$WP option get home

# Set an option
$WP option update blogname "My Site Name"

# List all autoloaded options with sizes
$WP db query "SELECT option_name, ROUND(LENGTH(option_value)/1024,1) AS kb FROM wp_options WHERE autoload='yes' ORDER BY kb DESC LIMIT 30"

# Total autoload size
$WP db query "SELECT ROUND(SUM(LENGTH(option_value))/1024) AS autoload_kb FROM wp_options WHERE autoload='yes'"

# Delete an option
$WP option delete [option_name]
```

---

## Transients

```bash
# Get a transient
$WP transient get [key]

# Delete a specific transient
$WP transient delete [key]

# Delete ALL transients (WordPress regenerates what it needs)
$WP transient delete --all

# Count orphaned transients
$WP db query "SELECT COUNT(*) FROM wp_options WHERE option_name LIKE '_transient_%'"
```

---

## Users

```bash
# List all users
$WP user list --format=table

# List admins only
$WP user list --role=administrator --fields=ID,user_login,user_email,registered --format=table

# Get a specific user
$WP user get [ID or login] --format=table

# Create a user
$WP user create username email@example.com --role=administrator --user_pass=password

# Update a user's password
$WP user update [ID] --user_pass='new-password'

# Change a user's role
$WP user set-role [ID] editor

# Delete a user (reassign posts to another user)
$WP user delete [ID] --reassign=[OTHER_ID]

# Rename a user (direct DB update — WP-CLI has no rename command)
$WP db query "UPDATE wp_users SET user_login='newname' WHERE user_login='oldname'"
```

---

## Posts & Content

```bash
# Count posts by type and status
$WP db query "SELECT post_type, post_status, COUNT(*) AS count FROM wp_posts GROUP BY post_type, post_status ORDER BY post_type, count DESC"

# List all revisions
$WP post list --post_type=revision --fields=ID,post_title,post_modified --format=table

# Delete all revisions
$WP post delete $(wp post list --post_type=revision --format=ids --allow-root) --force --allow-root

# List custom post type entries
$WP post list --post_type=service_areas --fields=ID,post_title,post_status --format=table

# Update a post's slug
$WP post update [ID] --post_name="new-slug"

# Update a post's status
$WP post update [ID] --post_status=publish

# Get a specific post's content
$WP post get [ID] --fields=post_title,post_content,post_status

# Bulk-update post meta
$WP post meta update [ID] [meta_key] [meta_value]
```

---

## Media

```bash
# List all media files
$WP media list --format=table

# Regenerate thumbnails
$WP media regenerate --yes

# Import a local image
$WP media import /path/to/image.jpg --title="Image Title" --post_id=[ID]
```

---

## Cron

```bash
# List scheduled cron events
$WP cron event list --fields=hook,next_run_relative,schedule --format=table

# Test cron system
$WP cron test

# Run all due cron events immediately
$WP cron event run --due-now

# Delete a cron event
$WP cron event delete [hook]
```

---

## Cache

```bash
# Flush the object cache
$WP cache flush

# Flush LiteSpeed Cache (if plugin active)
$WP litespeed-purge all
```

---

## Config (wp-config.php)

```bash
# List all constants in wp-config
$WP config list

# Get a specific constant
$WP config get WP_DEBUG

# Add or update a constant
$WP config set WP_DEBUG false --raw
$WP config set WP_POST_REVISIONS 5 --raw
$WP config set DISALLOW_FILE_EDIT true --raw

# Set a database variable
$WP config set DB_HOST 127.0.0.1
```

---

## Search Console / SEO (Rank Math)

```bash
# Force sitemap regeneration (Rank Math)
$WP rewrite flush

# Check permalink structure
$WP option get permalink_structure

# Reset permalink structure (fixes 404s after migration)
$WP rewrite structure '/%postname%/'
$WP rewrite flush
```

---

## Maintenance Mode

```bash
# Enable maintenance mode
$WP maintenance-mode activate

# Disable maintenance mode
$WP maintenance-mode deactivate

# Check maintenance mode status
$WP maintenance-mode status
```

---

## Eval (Run PHP Directly)

```bash
# Run a PHP snippet
$WP eval 'echo get_option("siteurl");'

# Run a PHP file
$WP eval-file /path/to/script.php

# Run a PHP file with stdin
cat script.php | $WP eval-file -
```

---

## Quick Aliases (add to .bashrc on server)

```bash
# If your WP path is fixed, set an alias
alias wp='wp --path=/home/u123456/domains/example.com/public_html --allow-root'

# Then just use:
wp plugin list
wp db export ~/backup.sql
```
