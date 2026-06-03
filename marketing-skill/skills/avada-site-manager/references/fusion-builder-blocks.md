# Avada Fusion Builder — Element Reference

Avada Builder 3.15.4

## Core Layout Elements

### Container `[fusion_builder_container]`
Top-level wrapper. Controls:
- Background (color, image, gradient, video)
- Padding (top/bottom/sides)
- Min-height
- Column layout within container

### Column `[fusion_builder_column]`
Divides containers into columns. Width: 1/1 to 1/6 fractions or custom %.

---

## Content Elements (common ones)

### Text Block `[fusion_text]`
Rich text / HTML content. Equivalent to a paragraph in Block Editor.
Use this for descriptive text sections.

### Heading `[fusion_title]`
H1–H6 with Avada styling (animated underline, icon, alignment).

### Button `[fusion_button]`
CTA buttons. Params: URL, text, size (small/medium/large), color, shape.
Primary CTA: `link="tel:+14157284163"` for click-to-call.

### Separator `[fusion_separator]`
Horizontal rule / spacer between sections.

### Spacer `[fusion_spacer]`
Blank vertical space with custom height.

### Image `[fusion_imageframe]`
Responsive image with lightbox, border, hover effects.

---

## Advanced Elements

### Flip Box `[fusion_flip_boxes]`
Front/back card flip on hover. Good for service listings.

### Counter Box `[fusion_counters_box]`
Animated number counter. Good for "134+ reviews", "95% success rate" etc.

### Accordion `[fusion_accordion]`
Collapsible FAQ sections. Use for neighborhood FAQ content.

### Tabs `[fusion_tabs]`
Tab-based content sections.

### Maps `[fusion_map]`
Google Maps embed (requires API key in Theme Options).

### Content Boxes `[fusion_content_boxes]`
Icon + heading + text cards. Good for service listings.

---

## SSA-Specific Usage Notes

### Service area pages
Service area pages use **Gutenberg blocks** for content, not Fusion Builder shortcodes.
Do NOT switch these pages to Avada Builder mode.

The Gutenberg block equivalents:
| Gutenberg | Fusion Builder |
|---|---|
| `<!-- wp:paragraph -->` | `[fusion_text]` |
| `<!-- wp:heading -->` | `[fusion_title]` |
| `<!-- wp:list -->` | `[fusion_text]` with `<ul>` |

### Homepage / landing pages
These CAN use Fusion Builder for layout sections (hero, features, etc.).

### Inserting Fusion elements into Block Editor pages
Do NOT mix shortcodes into Gutenberg-managed pages — they render as literal text in Block Editor.

---

## Avada Builder Shortcode Pattern
All Fusion elements follow this pattern:
```
[fusion_builder_container hundred_percent="no" equal_height_columns="no" hide_on_mobile="small-visibility,medium-visibility,large-visibility" background_color="" background_image="" background_position="center center" background_repeat="no-repeat" fade="no" background_parallax="none" enable_mobile="no" parallax_speed="0.3" video_mp4="" video_webm="" video_ogv="" video_url="" video_aspect_ratio="16:9" video_loop="yes" video_mute="yes" video_preview_image="" border_color="" border_style="solid" padding_top="" padding_bottom="" padding_left="" padding_right="" admin_label=""]

  [fusion_builder_row]
    [fusion_builder_column type="1_1" layout="1_1" spacing="" center_content="no" link="" target="_self" min_height="" hide_on_mobile="small-visibility,medium-visibility,large-visibility" class="" id="" hover_type="none" border_color="" border_style="solid" border_position="all" border_radius="" box_shadow="no" box_shadow_blur="0" box_shadow_spread="0" box_shadow_color="" box_shadow_style="" background_type="single" gradient_start_color="" gradient_end_color="" gradient_start_position="0" gradient_end_position="100" gradient_type="linear" radial_direction="center center" linear_angle="180" background_color="" background_image="" background_image_id="" background_position="left top" background_repeat="no-repeat" background_blend_mode="none" animation_type="" animation_direction="left" animation_speed="0.3" animation_offset="" filter_type="regular" filter_hue="0" filter_saturation="100" filter_brightness="100" filter_contrast="100" filter_invert="0" filter_sepia="0" filter_opacity="100" filter_blur="0" filter_hue_hover="0" filter_saturation_hover="100" filter_brightness_hover="100" filter_contrast_hover="100" filter_invert_hover="0" filter_sepia_hover="0" filter_opacity_hover="100" filter_blur_hover="0" last="true" first="true"]
      [fusion_text][/fusion_text]
    [/fusion_builder_column]
  [/fusion_builder_row]

[/fusion_builder_container]
```

When reading source of Avada Builder pages, this is what you'll see in `post_content`.
