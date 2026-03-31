#!/usr/bin/env python3
"""
Video Pipeline — Higgsfield AI
Generate videos from prompts.json or custom prompts.
Supports text-to-video, image-to-video, and batch processing.

Usage:
  python generate_video.py --category video_ai --output ./output
  python generate_video.py --prompt "cinematic drone shot over mountains" --model kling-2.0
  python generate_video.py --image input.png --prompt "animate this scene" --model kling-2.0
  python generate_video.py --batch batch_jobs.json --output ./output

Requires:
  pip install higgsfield-client python-dotenv
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
    print("Install: pip install higgsfield-client python-dotenv")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

PROMPTS_FILE = Path(__file__).parent / "prompts.json"
DEFAULT_OUTPUT = Path(__file__).parent / "output" / "video"

# ─── Available video models ──────────────────────────────────
MODELS = {
    "kling-2.0": "Kling 2.0 — fast, good quality",
    "kling-3.0": "Kling 3.0 — best quality, cinematic",
    "veo-3.1": "Google Veo 3.1 — realistic motion",
    "wan-2.5": "Wan 2.5 — creative/artistic",
    "sora-2": "OpenAI Sora 2 — text understanding",
    "minimax": "MiniMax — fast generation",
}


def load_prompts(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def resolve_variables(prompt_text: str, variables: dict, overrides: dict) -> str:
    merged = {**variables, **overrides}
    for key, value in merged.items():
        prompt_text = prompt_text.replace(f"{{{key}}}", str(value))
    return prompt_text


def parse_vars(vars_string: str) -> dict:
    if not vars_string:
        return {}
    result = {}
    for pair in vars_string.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k.strip()] = v.strip()
    return result


async def generate_video(client, prompt: str, model: str, duration: int,
                         output_dir: Path, name: str, image_path: str = None):
    """Generate a single video."""
    print(f"  🎬 Generating: {name}")
    print(f"     Model: {model} | Duration: {duration}s")
    print(f"     Prompt: {prompt[:80]}...")

    try:
        params = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
        }

        # Image-to-video mode
        if image_path:
            print(f"     Image: {image_path}")
            with open(image_path, "rb") as f:
                image_data = f.read()
            params["image"] = image_data

        result = await client.videos.generate(**params)

        # Save video
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.mp4"
        filepath = output_dir / filename

        # Download
        video_url = None
        if hasattr(result, 'videos') and result.videos:
            video_url = result.videos[0].url
        elif hasattr(result, 'url'):
            video_url = result.url
        elif isinstance(result, dict):
            video_url = result.get('url') or result.get('video_url')

        if video_url:
            import urllib.request
            urllib.request.urlretrieve(video_url, str(filepath))
            print(f"  ✅ Saved: {filepath}")
            return str(filepath)
        else:
            print(f"  ⚠️  No video URL in response")
            # Save raw response for debugging
            debug_path = output_dir / f"{name}_{timestamp}_response.json"
            with open(debug_path, "w") as f:
                json.dump(str(result), f)
            return None

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


async def process_batch(client, batch_file: str, output_dir: Path):
    """Process a batch JSON file with multiple video jobs."""
    with open(batch_file) as f:
        jobs = json.load(f)

    print(f"\n📋 Batch: {len(jobs)} jobs from {batch_file}")
    results = []

    for i, job in enumerate(jobs, 1):
        name = job.get("name", f"job_{i}")
        prompt = job["prompt"]
        model = job.get("model", "kling-2.0")
        duration = job.get("duration", 5)
        image = job.get("image", None)

        result = await generate_video(client, prompt, model, duration,
                                      output_dir, name, image)
        if result:
            results.append(result)

    return results


async def main():
    parser = argparse.ArgumentParser(description="Video Pipeline — Higgsfield AI")
    parser.add_argument("--category", "-c", help="Prompt category from prompts.json")
    parser.add_argument("--prompt", "-p", help="Custom prompt text")
    parser.add_argument("--model", "-m", default="kling-2.0",
                        choices=list(MODELS.keys()), help="Video model")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Duration in seconds")
    parser.add_argument("--image", "-i", help="Input image for image-to-video")
    parser.add_argument("--batch", "-b", help="Batch JSON file with video jobs")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), help="Output directory")
    parser.add_argument("--vars", "-v", default="", help="Override variables: key=val,key=val")
    parser.add_argument("--all-video", action="store_true", help="Generate all video prompts")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts without generating")
    args = parser.parse_args()

    if args.list_models:
        print("\n🎬 Available video models:\n")
        for k, v in MODELS.items():
            print(f"  {k:15s} — {v}")
        return

    output_dir = Path(args.output)
    overrides = parse_vars(args.vars)

    # Collect tasks
    tasks = []

    if args.batch:
        # Batch mode
        api_key = os.getenv("HIGGSFIELD_API_KEY")
        api_secret = os.getenv("HIGGSFIELD_API_SECRET")
        if not api_key or not api_secret:
            print("❌ Set HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET in .env")
            sys.exit(1)
        client = HiggsFieldClient(api_key=api_key, api_secret=api_secret)
        results = await process_batch(client, args.batch, output_dir)
        print(f"\n✅ Generated: {len(results)} videos")
        return

    if args.prompt:
        # Single custom prompt
        tasks.append(("custom", "custom_video", {
            "prompt": args.prompt,
            "model": args.model,
            "duration": args.duration,
            "type": "video"
        }))
    elif args.category or args.all_video:
        # From prompts.json
        prompts = load_prompts(PROMPTS_FILE)
        categories = prompts["categories"]

        if args.all_video:
            for cat_key, cat in categories.items():
                for p_key, p_data in cat["prompts"].items():
                    if p_data.get("type") == "video":
                        tasks.append((cat_key, p_key, p_data))
        elif args.category:
            if args.category not in categories:
                print(f"❌ Category not found. Available: {', '.join(categories.keys())}")
                sys.exit(1)
            cat = categories[args.category]
            for p_key, p_data in cat["prompts"].items():
                if p_data.get("type") == "video":
                    tasks.append((args.category, p_key, p_data))
    else:
        parser.print_help()
        sys.exit(0)

    if not tasks:
        print("⚠️  No video prompts found")
        sys.exit(0)

    print(f"\n{'='*50}")
    print(f"🎬 Video Pipeline — Higgsfield AI")
    print(f"📦 Tasks: {len(tasks)} videos")
    print(f"📁 Output: {output_dir}")
    print(f"{'='*50}\n")

    if args.dry_run:
        for cat, name, data in tasks:
            prompt = resolve_variables(data["prompt"], data.get("variables", {}), overrides)
            model = data.get("model", args.model)
            dur = data.get("duration", args.duration)
            print(f"[{cat}/{name}] {model} | {dur}s")
            print(f"  → {prompt}\n")
        return

    # Init client
    api_key = os.getenv("HIGGSFIELD_API_KEY")
    api_secret = os.getenv("HIGGSFIELD_API_SECRET")
    if not api_key or not api_secret:
        print("❌ Set HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET in .env")
        sys.exit(1)

    client = HiggsFieldClient(api_key=api_key, api_secret=api_secret)

    results = []
    for cat, name, data in tasks:
        prompt = resolve_variables(data["prompt"], data.get("variables", {}), overrides)
        model = data.get("model", args.model)
        duration = data.get("duration", args.duration)

        result = await generate_video(client, prompt, model, duration,
                                      output_dir / cat, name, args.image)
        if result:
            results.append(result)

    print(f"\n{'='*50}")
    print(f"✅ Generated: {len(results)}/{len(tasks)} videos")
    print(f"📁 Saved to: {output_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
