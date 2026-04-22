"""Download sprite model files from CivitAI into models/sprite/.

Usage:
    Add CIVITAI_TOKEN=your_token to config/.env, then:
    uv run python scripts/download_sprites.py
    uv run python scripts/download_sprites.py --token your_token
"""

import argparse
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "config" / ".env")

MODELS_DIR = Path(__file__).parent.parent / "models" / "sprite"

MODELS: list[dict] = [
    {
        "filename": "westernBeautiful_v10.safetensors",
        "version_id": "298593",
    },
    {
        "filename": "LCM_LoRA_Weights_SD15.safetensors",
        "version_id": "424706",
    },
    {
        "filename": "earthbound_lora.safetensors",
        "version_id": "188385",
    },
]

CHUNK_SIZE = 8 * 1024


def get_token(args: argparse.Namespace) -> str:
    token = args.token or os.environ.get("CIVITAI_TOKEN", "")
    if not token:
        print(
            "Error: CivitAI API token required.\n"
            "  Add CIVITAI_TOKEN=your_token to config/.env, or pass --token.\n"
            "  Get a free token at https://civitai.com/user/account"
        )
        sys.exit(1)
    return token


def resolve_download_url(model: dict, token: str) -> str:
    return f"https://civitai.com/api/download/models/{model['version_id']}?token={token}"


def download_file(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "llm-rpg-downloader/1.0"})
    with urllib.request.urlopen(req) as resp:
        if resp.status in (401, 403):
            print(f"Error: Authentication failed (HTTP {resp.status}). Check your token.")
            sys.exit(1)

        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0

        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    mb = downloaded / 1_048_576
                    total_mb = total / 1_048_576
                    print(f"\r  {pct:3d}%  {mb:.1f}/{total_mb:.1f} MB", end="", flush=True)

    print()


def file_needs_download(dest: Path, url: str) -> bool:
    if not dest.exists():
        return True
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "llm-rpg-downloader/1.0"})
    with urllib.request.urlopen(req) as resp:
        remote_size = int(resp.headers.get("Content-Length", -1))
    local_size = dest.stat().st_size
    return remote_size != local_size


def main() -> None:
    parser = argparse.ArgumentParser(description="Download sprite models from CivitAI")
    parser.add_argument("--token", help="CivitAI API token")
    args = parser.parse_args()

    token = get_token(args)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Saving models to: {MODELS_DIR}\n")

    for model in MODELS:
        filename = model["filename"]
        dest = MODELS_DIR / filename
        print(f"[{filename}]")

        url = resolve_download_url(model, token)

        if not file_needs_download(dest, url):
            print("  Already downloaded, skipping.\n")
            continue

        print(f"  Downloading...")
        download_file(url, dest)
        size_mb = dest.stat().st_size / 1_048_576
        print(f"  Saved ({size_mb:.1f} MB)\n")

    print("Done. Run `uv run python -m llm_rpg` to start the game.")


if __name__ == "__main__":
    main()
