#!/usr/bin/env python3
"""
caption_generator.py — GBP photo caption generator for local service businesses.

Generates Google Business Profile photo captions by photo type.
Each photo type gets 2-3 caption variations to avoid duplicate content.

Usage:
    python3 caption_generator.py [--config config.json] [--type all|team|job|equipment|storefront|before-after]
    python3 caption_generator.py               (sample demo, all caption types)

Config JSON: same format as post_generator.py

Photo types:
    team         — Technician or team photos
    job          — In-progress or completed repair photos
    before-after — Side-by-side or labeled before/after shots
    equipment    — Tools, parts, van, equipment
    storefront   — Office, front door, signage (for businesses with a location)
"""

import json
import sys
import argparse
from typing import Dict, List


# ─── Caption builders ─────────────────────────────────────────────────────────

def captions_team(c: Dict) -> List[Dict]:
    name = c["business_name"]
    city = c["city"]
    service = c.get("primary_service", "appliance repair")
    areas = c.get("service_areas", [city])
    area_str = ", ".join(areas[:3])

    return [
        {
            "label": "Team — Professional intro",
            "caption": (
                f"{name} technician — licensed, insured, and background-checked. "
                f"Our team services all major appliance brands across {area_str}. "
                f"Ready to diagnose and fix your appliance, often the same day you call."
            ),
        },
        {
            "label": "Team — Trust + experience",
            "caption": (
                f"Meet the {name} team. Every technician is trained on all major brands, "
                f"carries full liability insurance, and uses genuine OEM parts. "
                f"When your appliance breaks, you deserve a professional — not a guess. "
                f"Serving {city} and the surrounding area."
            ),
        },
        {
            "label": "Team — Local angle",
            "caption": (
                f"{name} — locally owned and operated in {city}. "
                f"Our technicians live and work in this community. "
                f"Fast response times because we're already nearby. "
                f"Same-day {service} available across {area_str}."
            ),
        },
    ]


def captions_job(c: Dict) -> List[Dict]:
    name = c["business_name"]
    city = c["city"]
    warranty = c.get("warranty_days", 90)
    service = c.get("primary_service", "appliance repair")

    return [
        {
            "label": "Job — In-progress repair",
            "caption": (
                f"{service.capitalize()} in progress — {city}. "
                f"{name} technician diagnosing the issue on-site. "
                f"Most repairs are completed in a single visit using OEM parts stocked in our van. "
                f"All repairs backed by a {warranty}-day parts and labor warranty."
            ),
        },
        {
            "label": "Job — Completed repair",
            "caption": (
                f"Another appliance back in service — {city}. "
                f"{name} completed this repair same-day. "
                f"We always test the appliance through a full cycle before leaving. "
                f"{warranty}-day warranty on all parts and labor."
            ),
        },
        {
            "label": "Job — Diagnostic focus",
            "caption": (
                f"Thorough diagnostics before any repair. "
                f"{name} technicians identify the root cause — not just the symptom — "
                f"so the fix lasts. Serving {city} and surrounding areas. "
                f"Same-day appointments available."
            ),
        },
    ]


def captions_before_after(c: Dict) -> List[Dict]:
    name = c["business_name"]
    warranty = c.get("warranty_days", 90)

    return [
        {
            "label": "Before/After — Standard",
            "caption": (
                f"Before and after: [describe the appliance, brand, and problem]. "
                f"[Describe what was wrong and what was replaced or fixed.] "
                f"Back in service same day. "
                f"All {name} repairs include a {warranty}-day parts and labor warranty."
            ),
        },
        {
            "label": "Before/After — Brand-specific",
            "caption": (
                f"[Brand] [appliance type] repair — [City]. "
                f"[Describe the symptom: e.g., 'stopped draining', 'not cooling', 'making grinding noise'.] "
                f"[What {name} found and fixed.] "
                f"Completed in one visit using genuine OEM parts. "
                f"{warranty}-day warranty included."
            ),
        },
        {
            "label": "Before/After — Problem-solution format",
            "caption": (
                f"Problem: [appliance] [symptom]. "
                f"Solution: [part replaced or repair performed]. "
                f"Result: [outcome, e.g., running quietly / cooling properly / draining again]. "
                f"{name} — same-day appliance repair with a {warranty}-day warranty."
            ),
        },
    ]


def captions_equipment(c: Dict) -> List[Dict]:
    name = c["business_name"]
    city = c["city"]
    brands = c.get("brands", [])
    luxury = [b for b in brands if b in ("Sub-Zero", "Wolf", "Miele", "Thermador", "Viking")]
    service = c.get("primary_service", "appliance repair")

    parts_line = (
        f"We stock genuine OEM parts for {', '.join(luxury[:3])} and all major brands"
        if luxury else
        f"We stock genuine OEM parts for all major appliance brands"
    )

    return [
        {
            "label": "Equipment — OEM parts",
            "caption": (
                f"{parts_line} — so most repairs are completed in a single visit. "
                f"No waiting for parts to ship. {name} — same-day {service} in {city}."
            ),
        },
        {
            "label": "Equipment — Service van",
            "caption": (
                f"The {name} service van — stocked with parts and tools for same-day repairs. "
                f"We carry inventory for all major brands so we can fix your appliance without a return trip. "
                f"Serving {city} and the surrounding area."
            ),
        },
        {
            "label": "Equipment — Diagnostic tools",
            "caption": (
                f"Professional-grade diagnostic equipment. "
                f"{name} technicians use the same tools as factory-authorized service centers — "
                f"multimeters, refrigerant gauges, and brand-specific diagnostic software. "
                f"Accurate diagnosis means the repair gets done right the first time."
            ),
        },
    ]


def captions_storefront(c: Dict) -> List[Dict]:
    name = c["business_name"]
    city = c["city"]
    phone = c["phone"]
    service = c.get("primary_service", "appliance repair")
    areas = c.get("service_areas", [city])
    area_str = ", ".join(areas[:3])

    return [
        {
            "label": "Storefront — Welcome",
            "caption": (
                f"{name} — {service} serving {area_str}. "
                f"Licensed, insured, and family-owned. "
                f"Call {phone} for same-day appointments."
            ),
        },
        {
            "label": "Storefront — Local + trust",
            "caption": (
                f"Locally owned in {city}. "
                f"{name} has been serving {city} residents with professional {service}. "
                f"Fast, reliable, and backed by a 90-day warranty. "
                f"Call {phone} or book online."
            ),
        },
    ]


CAPTION_BUILDERS = {
    "team": captions_team,
    "job": captions_job,
    "before-after": captions_before_after,
    "equipment": captions_equipment,
    "storefront": captions_storefront,
}

PHOTO_TYPE_LABELS = {
    "team": "TEAM / TECHNICIAN PHOTOS",
    "job": "JOB / IN-PROGRESS PHOTOS",
    "before-after": "BEFORE & AFTER PHOTOS",
    "equipment": "EQUIPMENT / PARTS / VAN PHOTOS",
    "storefront": "STOREFRONT / OFFICE PHOTOS",
}


# ─── Formatter ────────────────────────────────────────────────────────────────

def format_captions(photo_type: str, captions: List[Dict]) -> str:
    lines = [
        "=" * 65,
        PHOTO_TYPE_LABELS.get(photo_type, photo_type.upper()),
        "=" * 65,
        "",
    ]
    for cap in captions:
        char_count = len(cap["caption"])
        lines.append(f"── {cap['label']}  ({char_count} chars / 1500 max)")
        lines.append(cap["caption"])
        lines.append("")
    return "\n".join(lines)


# ─── Sample config ────────────────────────────────────────────────────────────

SAMPLE_CONFIG = {
    "business_name": "Smart Solution Appliances",
    "phone": "(415) 728-4163",
    "website": "https://smartsolutionappliances.com",
    "primary_service": "appliance repair",
    "brands": ["Samsung", "LG", "Whirlpool", "GE", "Bosch", "Sub-Zero", "Wolf", "Miele"],
    "city": "San Francisco",
    "service_areas": ["San Francisco", "Marin County", "Peninsula"],
    "warranty_days": 90,
    "emojis": False,
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GBP photo caption generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", help="Path to business config JSON")
    parser.add_argument(
        "--type",
        choices=["all"] + list(CAPTION_BUILDERS.keys()),
        default="all",
        help="Photo type to generate captions for (default: all)",
    )
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = SAMPLE_CONFIG
        print("[INFO] No --config provided. Using sample data.\n", file=sys.stderr)

    types = list(CAPTION_BUILDERS.keys()) if args.type == "all" else [args.type]

    print(f"GBP Photo Captions — {config['business_name']}")
    print(f"Each type includes 2-3 variations. Pick the one that fits your photo best.")
    print()

    for photo_type in types:
        captions = CAPTION_BUILDERS[photo_type](config)
        print(format_captions(photo_type, captions))

    print("─" * 65)
    print("GBP caption max: 1,500 characters.")
    print("For before/after captions: fill in the [bracketed] fields with your specific job details.")


if __name__ == "__main__":
    main()
