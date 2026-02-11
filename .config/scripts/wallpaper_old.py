import json
import random
import re
import subprocess
from pathlib import Path

import fast_colorthief  # pip install fast-colorthief

# Note that CMake must be installed. If there is ever a problem during the installation of the module, run: `export CMAKE_POLICY_VERSION_MINIMUM=3.5`

IMAGE_FOLDER = "~/Pictures/wallpapers"
CACHE_FILE = "~/.cache/wallpaper_colors.json"
COLOR_COUNT = 4
BASH_COMMANDS = [('swww img "{PATH}"', False), ("killall -SIGUSR2 waybar", False)]

CONFIG_UPDATES = {
    "~/.config/niri/config.kdl": [
        {
            "pattern": r'active-gradient from="[^"]*" to="[^"]*"',
            "template": lambda colors: f'active-gradient from="#{colors[0][0]:02x}{colors[0][1]:02x}{colors[0][2]:02x}" to="#{colors[1][0]:02x}{colors[1][1]:02x}{colors[1][2]:02x}"',
        },
        {
            "pattern": r'inactive-gradient from="[^"]*" to="[^"]*"',
            "template": lambda colors: f'inactive-gradient from="#{colors[2][0]:02x}{colors[2][1]:02x}{colors[2][2]:02x}" to="#{colors[3][0]:02x}{colors[3][1]:02x}{colors[3][2]:02x}"',
        },
    ],
    "~/.config/waybar/style.css": [
        {
            "pattern": r"border-color:\s*#[0-9a-fA-F]{6};",
            "template": lambda dominant: f"border-color: #{dominant[0]:02x}{dominant[1]:02x}{dominant[2]:02x};",
        }
    ],
}


def load_cache() -> dict:
    if not (path := Path(CACHE_FILE).expanduser()).exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return {}


def get_image_key(image_path: Path) -> str:
    st = image_path.stat()
    return (
        f"{image_path.expanduser().resolve().as_posix()}_{st.st_mtime_ns}_{st.st_size}"
    )


def get_cached_colors(
    image_path: Path,
) -> tuple[list[list[int, int, int]], list[int, int, int]] | None:
    if entry := load_cache().get(get_image_key(image_path)):
        return entry["palette"], entry["dominant"]


def set_cached_colors(
    image_path: Path,
    palette: list[tuple[int, int, int]],
    dominant: tuple[int, int, int],
):
    cache = load_cache()
    cache[get_image_key(image_path)] = {"palette": palette, "dominant": dominant}
    path = Path(CACHE_FILE).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def get_random_image(folder_path: str) -> Path | None:
    folder = Path(folder_path).expanduser()
    image_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".avif",
        ".gif",
        ".pnm",
        ".tga",
        ".tiff",
        ".webp",
        ".bmp",
        ".farbfeld",
    }
    images = [f for f in folder.glob("*") if f.suffix.lower() in image_extensions]
    return random.choice(images) if images else None


def extract_colors(
    image_path: Path,
) -> tuple[list[tuple[int, int, int]], tuple[int, int, int]]:
    if cached := get_cached_colors(image_path):
        return cached
    palette = fast_colorthief.get_palette(str(image_path), color_count=COLOR_COUNT)
    dominant = fast_colorthief.get_dominant_color(str(image_path), quality=1)
    set_cached_colors(image_path, palette, dominant)
    return palette, dominant


def lighten_color(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(min(int(c + (255 - c) * amount), 255) for c in color)


def darken_color(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(max(int(c * (1 - amount)), 0) for c in color)


def update_file(
    file_path: Path,
    updates: list[dict],
    palette: list[tuple[int, int, int]],
    dominant: tuple[int, int, int],
):
    path = Path(file_path).expanduser()
    if not path.exists():
        return

    content = path.read_text()

    for update in updates:
        if "dominant" in update["template"].__code__.co_varnames:
            replacement = update["template"](dominant)
        else:
            replacement = update["template"](palette)

        content = re.sub(update["pattern"], replacement, content)

    path.write_text(content)


def run_commands(commands: list[tuple[str, bool]], image: Path):
    for cmd, is_background in commands:
        if is_background:
            subprocess.Popen(
                cmd.replace("{PATH}", image.as_posix()),
                shell=True,
                start_new_session=True,
            )
        else:
            subprocess.run(
                cmd.replace("{PATH}", image.as_posix()), shell=True, check=True
            )


def main():
    image = get_random_image(IMAGE_FOLDER)
    if not image:
        return

    palette, dominant = extract_colors(image)
    palette_sorted = sorted(palette, key=lambda c: sum(c))
    palette = [lighten_color(c, 0.1) for c in palette_sorted[COLOR_COUNT // 2 :]] + [
        darken_color(c, 0.2) for c in palette_sorted[: COLOR_COUNT // 2]
    ]
    dominant = lighten_color(dominant, 0.3)

    for file_path, updates in CONFIG_UPDATES.items():
        update_file(file_path, updates, palette, dominant)

    run_commands(BASH_COMMANDS, image)


if __name__ == "__main__":
    main()
