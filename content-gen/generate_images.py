#!/usr/bin/env python3
"""
Batch Image Generator — Higgsfield AI
Reads prompts from prompts.json and generates images in batch.

Usage:
  python generate_images.py --category saas --output ./output
  python generate_images.py --category landing --prompt hero_background --vars "color_1=red,color_2=orange"
  python generate_images.py --all --output ./output

Requires:
  pip install higgsfield-client python-dotenv
  
Environment:
  HIGGSFIELD_API_KEY=your_api_key
  HIGGSFIELD_API_SECRET=your_api_secret
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from higgsfield import HiggsFieldClient
except ImportError:
    print("Install higgsfield-client: pip install higgsfield-client")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

# ─── Config ───────────────────────────────────────────────────
PROMPTS_FILE = Path(__file__).parent / "prompts.json"
DEFAULT_OUTPUT = Path(__file__).parent / "output"


def load_prompts(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def resolve_variables(prompt_text: str, variables: dict, overrides: dict) -> str:
    """Replace {variable} placeholders in prompt text."""
    merged = {**variables, **overrides}
    for key, value in merged.items():
        prompt_text = prompt_text.replace(f"{{{key}}}", str(value))
    return prompt_text


def parse_vars(vars_string: str) -> dict:
    """Parse 'key1=val1,key2=val2' into dict."""
    if not vars_string:
        return {}
    result = {}
    for pair in vars_string.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k.strip()] = v.strip()
    return result


async def generate_image(client, prompt_data: dict, name: str, output_dir: Path, overrides: dict):
    """Generate a single image using Higgsfield API."""
    if prompt_data.get("type") == "video":
        print(f"  ⏭  Skipping {name} (video prompt, use generate_video.py)")
        return None

    prompt_text = prompt_data["prompt"]
    variables = prompt_data.get("variables", {})
    prompt_text = resolve_variables(prompt_text, variables, overrides)

    model = prompt_data.get("model", "flux-1.1-pro")
    aspect = prompt_data.get("aspect_ratio", "1:1")
    negative = prompt_data.get("negative_prompt", "")

    print(f"  🎨 Generating: {name}")
    print(f"     Model: {model} | Aspect: {aspect}")
    print(f"     Prompt: {prompt_text[:80]}...")

    try:
        result = await client.images.generate(
            model=model,
            prompt=prompt_text,
            negative_prompt=negative,
            aspect_ratio=aspect,
            num_images=1,
        )

        # Save image
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = output_dir / filename

        # Download and save
        if hasattr(result, 'images') and result.images:
            image_url = result.images[0].url
            import urllib.request
            urllib.request.urlretrieve(image_url, str(filepath))
            print(f"  ✅ Saved: {filepath}")
            return str(filepath)
        elif hasattr(result, 'url'):
            import urllib.request
            urllib.request.urlretrieve(result.url, str(filepath))
            print(f"  ✅ Saved: {filepath}")
            return str(filepath)
        else:
            print(f"  ⚠️  No image in response for {name}")
            return None

    except Exception as e:
        print(f"  ❌ Error generating {name}: {e}")
        return None


async def main():
    parser = argparse.ArgumentParser(description="Batch Image Generator — Higgsfield AI")
    parser.add_argument("--category", "-c", help="Prompt category (saas, landing, video_ai, bots)")
    parser.add_argument("--prompt", "-p", help="Specific prompt name within category")
    parser.add_argument("--all", action="store_true", help="Generate all image prompts")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), help="Output directory")
    parser.add_argument("--vars", "-v", default="", help="Override variables: key1=val1,key2=val2")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts without generating")
    args = parser.parse_args()

    # Load prompts
    prompts = load_prompts(PROMPTS_FILE)
    categories = prompts["categories"]
    overrides = parse_vars(args.vars)
    output_dir = Path(args.output)

    # Collect prompts to generate
    tasks = []
    if args.all:
        for cat_key, cat in categories.items():
            for p_key, p_data in cat["prompts"].items():
                tasks.append((cat_key, p_key, p_data))
    elif args.category:
        if args.category not in categories:
            print(f"❌ Category '{args.category}' not found. Available: {', '.join(categories.keys())}")
            sys.exit(1)
        cat = categories[args.category]
        if args.prompt:
            if args.prompt not in cat["prompts"]:
                print(f"❌ Prompt '{args.prompt}' not found in {args.category}")
                sys.exit(1)
            tasks.append((args.category, args.prompt, cat["prompts"][args.prompt]))
        else:
            for p_key, p_data in cat["prompts"].items():
                tasks.append((args.category, p_key, p_data))
    else:
        parser.print_help()
        sys.exit(0)

    print(f"\n{'='*50}")
    print(f"🖼  Batch Image Generator — Higgsfield AI")
    print(f"📦 Tasks: {len(tasks)} images to generate")
    print(f"📁 Output: {output_dir}")
    print(f"{'='*50}\n")

    if args.dry_run:
        for cat, name, data in tasks:
            if data.get("type") == "video":
                continue
            prompt = resolve_variables(data["prompt"], data.get("variables", {}), overrides)
            print(f"[{cat}/{name}] {data.get('model', 'flux-1.1-pro')} | {data.get('aspect_ratio', '1:1')}")
            print(f"  → {prompt}\n")
        return

    # Initialize client
    api_key = os.getenv("HIGGSFIELD_API_KEY")
    api_secret = os.getenv("HIGGSFIELD_API_SECRET")
    if not api_key or not api_secret:
        print("❌ Set HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET in .env")
        sys.exit(1)

    client = HiggsFieldClient(api_key=api_key, api_secret=api_secret)

    results = []
    for cat, name, data in tasks:
        cat_output = output_dir / cat
        result = await generate_image(client, data, name, cat_output, overrides)
        if result:
            results.append(result)

    print(f"\n{'='*50}")
    print(f"✅ Generated: {len(results)}/{len(tasks)} images")
    print(f"📁 Saved to: {output_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
