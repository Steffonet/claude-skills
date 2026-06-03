#!/usr/bin/env python3
"""
post_generator.py — GBP weekly post generator for local service businesses.

Generates Google Business Profile posts for all 4 rotating topics, identifies
this week's topic by ISO week number, and outputs ready-to-publish content.

Usage:
    python3 post_generator.py [--config config.json] [--mode posts|qa|all] [--week N]
    python3 post_generator.py                          (sample demo, this week's post)
    python3 post_generator.py --mode all               (all 4 posts + 10 Q&A pairs)

Config JSON format:
    {
        "business_name": "Smart Solution Appliances",
        "phone": "(415) 728-4163",
        "website": "https://smartsolutionappliances.com",
        "booking_url": "https://booking.example.com",
        "brands_page_url": "https://smartsolutionappliances.com/brands/",
        "primary_service": "appliance repair",
        "appliances": ["washers", "dryers", "refrigerators", "dishwashers", "ovens"],
        "brands": ["Samsung", "LG", "Whirlpool", "GE", "Bosch", "Sub-Zero", "Wolf", "Miele"],
        "city": "San Francisco",
        "service_areas": ["San Francisco", "Marin County", "Peninsula"],
        "diagnostic_fee": "$95",
        "warranty_days": 90,
        "years_in_business": 10,
        "differentiators": ["same-day service", "licensed and insured", "90-day warranty", "OEM parts"],
        "emojis": true
    }
"""

import json
import sys
import datetime
import argparse
from typing import Dict, List, Optional


# ─── Topic definitions ────────────────────────────────────────────────────────

TOPIC_LABELS = {
    1: "Emergency / Speed",
    2: "Brand / Expertise",
    3: "Trust / Warranty",
    0: "Full Service Range",
}


def get_this_week_topic() -> int:
    return datetime.date.today().isocalendar()[1] % 4


# ─── Post builders ────────────────────────────────────────────────────────────

def post_speed(c: Dict) -> Dict:
    name = c["business_name"]
    phone = c["phone"]
    city = c["city"]
    areas = " | ".join(c.get("service_areas", [city]))
    appliance_list = ", ".join(c.get("appliances", ["washers", "dryers", "refrigerators", "dishwashers", "ovens"]))
    diag = c.get("diagnostic_fee", "")
    warranty = c.get("warranty_days", 90)
    brands_snippet = ", ".join(c.get("brands", ["all major brands"])[:5])
    e = "" if not c.get("emojis", True) else "🔧 "

    diag_line = f"\n{e or ''}Diagnostic fee waived when you approve the repair" if diag else ""
    warranty_line = f"\n{'✅ ' if c.get('emojis') else ''}{warranty}-day warranty on all parts and labor"
    brands_line = f"\n{'✅ ' if c.get('emojis') else ''}{brands_snippet} & all major brands serviced"

    content = (
        f"{e}Appliance down? We come the same day.\n\n"
        f"{name} covers {city} and the surrounding area with fast {c.get('primary_service', 'appliance repair')}. "
        f"Our licensed technicians fix {appliance_list} — usually within hours of your call.\n"
        f"{diag_line}{warranty_line}{brands_line}\n\n"
        f"Don't wait. Call {phone} for same-day service."
    )
    return {
        "topic": "Emergency / Speed",
        "content": content.strip(),
        "cta_type": "CALL",
        "cta_url": None,
        "char_count": len(content.strip()),
    }


def post_expertise(c: Dict) -> Dict:
    name = c["business_name"]
    city = c["city"]
    brands = c.get("brands", [])
    luxury_brands = [b for b in brands if b in ("Sub-Zero", "Wolf", "Miele", "Thermador", "Viking", "Gaggenau", "Bosch")]
    brands_page = c.get("brands_page_url", c.get("website", ""))
    warranty = c.get("warranty_days", 90)
    e_head = "🏆 " if c.get("emojis") else ""
    e_check = "✅ " if c.get("emojis") else ""

    if luxury_brands:
        brand_str = ", ".join(luxury_brands)
        hook = f"{e_head}{luxury_brands[0]} broken? That needs a specialist."
        body = (
            f"{name} trains on luxury appliance brands — {brand_str}. "
            f"We stock genuine OEM parts and diagnose at the manufacturer level, "
            f"without the manufacturer wait times."
        )
    else:
        brand_str = ", ".join(brands[:4]) if brands else "all major brands"
        hook = f"{e_head}Expert {c.get('primary_service', 'appliance repair')} in {city}."
        body = (
            f"{name} technicians train on {brand_str} and all major appliance brands. "
            f"We stock genuine OEM parts and complete most repairs in a single visit."
        )

    certs = f"\n{e_check}Certified for premium brands" if luxury_brands else ""
    content = (
        f"{hook}\n\n"
        f"{body}\n"
        f"{certs}"
        f"\n{e_check}Same-day service across {city}"
        f"\n{e_check}{warranty}-day warranty on every repair"
        f"\n\nLearn about the brands we service →"
    )
    return {
        "topic": "Brand / Expertise",
        "content": content.strip(),
        "cta_type": "LEARN_MORE",
        "cta_url": brands_page,
        "char_count": len(content.strip()),
    }


def post_trust(c: Dict) -> Dict:
    name = c["business_name"]
    phone = c["phone"]
    booking = c.get("booking_url", c.get("website", ""))
    city = c["city"]
    areas = c.get("service_areas", [city])
    warranty = c.get("warranty_days", 90)
    e_shield = "🛡️ " if c.get("emojis") else ""
    e_pin = "📍 " if c.get("emojis") else ""

    area_str = ", ".join(areas[:3])
    content = (
        f"{e_shield}Every repair comes with a {warranty}-day warranty. No exceptions.\n\n"
        f"If anything related to our repair fails within {warranty} days, we come back at no charge. "
        f"We use genuine OEM parts — not aftermarket substitutes — and our technicians are "
        f"licensed, insured, and background-checked.\n\n"
        f"{e_pin}Serving {area_str}\n\n"
        f"Ready to book a repair that lasts?\n{phone}"
    )
    return {
        "topic": "Trust / Warranty",
        "content": content.strip(),
        "cta_type": "BOOK",
        "cta_url": booking,
        "char_count": len(content.strip()),
    }


def post_full_range(c: Dict) -> Dict:
    name = c["business_name"]
    phone = c["phone"]
    city = c["city"]
    areas = c.get("service_areas", [city])
    appliances = c.get("appliances", ["washers", "dryers", "refrigerators", "dishwashers", "ovens"])
    brands = c.get("brands", [])
    e_wrench = "🔩 " if c.get("emojis") else ""
    e_pin = "📍 " if c.get("emojis") else ""

    appliance_bullets = "\n".join(f"• {a.capitalize()}" for a in appliances)
    brand_str = ", ".join(brands) if brands else "all major brands"
    area_str = " | ".join(areas)

    content = (
        f"{e_wrench}Whatever's broken — we fix it.\n\n"
        f"{name} repairs every major home appliance:\n"
        f"{appliance_bullets}\n\n"
        f"All brands: {brand_str}.\n\n"
        f"{e_pin}{area_str}\n"
        f"{phone} — same-day appointments available"
    )
    return {
        "topic": "Full Service Range",
        "content": content.strip(),
        "cta_type": "CALL",
        "cta_url": None,
        "char_count": len(content.strip()),
    }


POST_BUILDERS = {1: post_speed, 2: post_expertise, 3: post_trust, 0: post_full_range}


# ─── Q&A builder ──────────────────────────────────────────────────────────────

def build_qa(c: Dict) -> List[Dict]:
    name = c["business_name"]
    phone = c["phone"]
    website = c.get("website", "")
    city = c["city"]
    areas = c.get("service_areas", [city])
    diag = c.get("diagnostic_fee", "$75-$95")
    warranty = c.get("warranty_days", 90)
    brands = c.get("brands", [])
    brand_str = ", ".join(brands[:8]) if brands else "all major brands"
    appliances = c.get("appliances", ["washers", "dryers", "refrigerators", "dishwashers", "ovens"])
    service_str = ", ".join(appliances)
    area_str = ", ".join(areas[:4])
    state = c.get("state", "California")

    return [
        {
            "question": f"How much does appliance repair cost in {city}?",
            "answer": (
                f"Diagnostic fee is {diag}, which is waived when you approve the repair. "
                f"Most repairs run $150-$350 depending on the appliance and the part needed. "
                f"We provide a written estimate before any work begins — no surprises."
            ),
        },
        {
            "question": f"Do you offer same-day appliance repair in {city}?",
            "answer": (
                f"Yes. Call before noon and we can typically schedule a same-day appointment "
                f"across {city} and the surrounding area. Evening appointments are also available."
            ),
        },
        {
            "question": "What appliance brands do you service?",
            "answer": (
                f"All major brands: {brand_str}, and more. "
                f"If you own it, we most likely service it. Call {phone} to confirm."
            ),
        },
        {
            "question": "Do you offer a warranty on appliance repairs?",
            "answer": (
                f"Yes — {warranty}-day parts and labor warranty on every repair. "
                f"If anything related to our work fails within {warranty} days, "
                f"we return at no charge."
            ),
        },
        {
            "question": "Are your technicians licensed and insured?",
            "answer": (
                f"Yes. All {name} technicians are fully licensed, bonded, and insured in {state}. "
                f"We carry liability insurance on every job."
            ),
        },
        {
            "question": "Which appliances do you repair?",
            "answer": (
                f"We repair: {service_str}. "
                f"We handle both freestanding and built-in units across all major brands."
            ),
        },
        {
            "question": "Do you repair appliances at my home, or do I bring them to you?",
            "answer": (
                f"{name} is an in-home service — we diagnose and repair at your location. "
                f"No need to haul heavy appliances anywhere. We come to you."
            ),
        },
        {
            "question": "How do I schedule a repair?",
            "answer": (
                f"Call {phone} or book online at {website}. "
                f"We'll confirm a time window and send a technician to your door."
            ),
        },
        {
            "question": "What areas do you serve?",
            "answer": (
                f"We serve {area_str}. "
                f"Call {phone} to confirm your specific location is covered."
            ),
        },
        {
            "question": "What should I do if my appliance breaks on a weekend?",
            "answer": (
                f"Call {phone} — we offer weekend appointments. "
                f"Saturday same-day availability applies; call early for the best time slot."
            ),
        },
    ]


# ─── Formatters ───────────────────────────────────────────────────────────────

def format_post(post: Dict, highlight: bool = False) -> str:
    lines = []
    marker = " ◀ THIS WEEK" if highlight else ""
    lines.append(f"{'='*65}")
    lines.append(f"TOPIC: {post['topic']}{marker}")
    lines.append(f"Characters: {post['char_count']} / 1500")
    lines.append(f"CTA: {post['cta_type']}" + (f"  →  {post['cta_url']}" if post['cta_url'] else ""))
    lines.append(f"{'─'*65}")
    lines.append(post["content"])
    lines.append("")
    return "\n".join(lines)


def format_qa(qa_pairs: List[Dict]) -> str:
    lines = ["=" * 65, "GBP Q&A SEEDS — Copy-paste directly into your GBP Q&A section", "=" * 65, ""]
    for i, pair in enumerate(qa_pairs, 1):
        lines.append(f"Q{i}: {pair['question']}")
        lines.append(f"A:  {pair['answer']}")
        lines.append("")
    lines.append("─" * 65)
    lines.append("Post these in your Google Business Profile → Q&A section.")
    lines.append("You write BOTH the question and the answer.")
    return "\n".join(lines)


# ─── Sample config ────────────────────────────────────────────────────────────

SAMPLE_CONFIG = {
    "business_name": "Smart Solution Appliances",
    "phone": "(415) 728-4163",
    "website": "https://smartsolutionappliances.com",
    "booking_url": "https://app.jobber.com/newrequest?id=9e6db754",
    "brands_page_url": "https://smartsolutionappliances.com/brands/",
    "primary_service": "appliance repair",
    "appliances": ["washers", "dryers", "refrigerators", "dishwashers", "ovens", "microwaves", "ice makers"],
    "brands": ["Samsung", "LG", "Whirlpool", "GE", "Bosch", "Maytag", "KitchenAid", "Sub-Zero", "Wolf", "Miele"],
    "city": "San Francisco",
    "state": "California",
    "service_areas": ["San Francisco", "Marin County", "Peninsula", "East Bay"],
    "diagnostic_fee": "$95",
    "warranty_days": 90,
    "years_in_business": 10,
    "emojis": True,
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GBP weekly post generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", help="Path to business config JSON")
    parser.add_argument(
        "--mode",
        choices=["posts", "qa", "all"],
        default="posts",
        help="Output mode: posts (default), qa, or all",
    )
    parser.add_argument(
        "--week",
        type=int,
        choices=[0, 1, 2, 3],
        help="Override week mod (0-3) instead of using today's ISO week",
    )
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = SAMPLE_CONFIG
        print("[INFO] No --config provided. Using sample data.\n", file=sys.stderr)

    this_week = args.week if args.week is not None else get_this_week_topic()
    today = datetime.date.today()
    iso_week = today.isocalendar()[1]

    print(f"GBP Content Generator  —  {today.strftime('%B %d, %Y')}")
    print(f"ISO Week {iso_week}  →  This week's topic: {TOPIC_LABELS[this_week]}")
    print()

    if args.mode in ("posts", "all"):
        print("4-WEEK POST ROTATION")
        print()
        for topic_key in [1, 2, 3, 0]:
            post = POST_BUILDERS[topic_key](config)
            print(format_post(post, highlight=(topic_key == this_week)))

    if args.mode in ("qa", "all"):
        qa = build_qa(config)
        print(format_qa(qa))


if __name__ == "__main__":
    main()
