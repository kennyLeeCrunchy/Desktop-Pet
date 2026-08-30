from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


FRAME_WIDTH = 192
FRAME_HEIGHT = 208


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: prepare_assets.py <spritesheet.webp> <asset-directory>"
        )

    source = Path(sys.argv[1])
    asset_dir = Path(sys.argv[2])
    asset_dir.mkdir(parents=True, exist_ok=True)

    atlas = Image.open(source).convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"Unexpected v2 atlas size: {atlas.size}")

    atlas.save(asset_dir / "spritesheet.png", optimize=True)

    idle = atlas.crop((0, 0, FRAME_WIDTH, FRAME_HEIGHT))
    bbox = idle.getbbox()
    if bbox:
        idle = idle.crop(bbox)
    idle.thumbnail((220, 220), Image.Resampling.LANCZOS)

    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    x = (256 - idle.width) // 2
    y = (256 - idle.height) // 2
    icon.alpha_composite(idle, (x, y))
    icon.save(
        asset_dir / "galgyo.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    print(f"Prepared assets in {asset_dir}")


if __name__ == "__main__":
    main()

