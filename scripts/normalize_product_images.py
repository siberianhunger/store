from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "media" / "separate_samples"
OUTPUT_DIR = ROOT / "media" / "catalog_samples"
TARGET_SIZE = (900, 1200)
BACKGROUND = (8, 34, 51)
INNER_PADDING = 54


def normalize_image(source_path, output_path):
    source = Image.open(source_path).convert("RGB")
    max_width = TARGET_SIZE[0] - INNER_PADDING * 2
    max_height = TARGET_SIZE[1] - INNER_PADDING * 2
    source.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", TARGET_SIZE, BACKGROUND)
    left = (TARGET_SIZE[0] - source.width) // 2
    top = (TARGET_SIZE[1] - source.height) // 2
    canvas.paste(source, (left, top))
    canvas.save(output_path, optimize=True)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(1, 17):
        normalize_image(
            SOURCE_DIR / f"stone{index}.png",
            OUTPUT_DIR / f"stone{index}.png",
        )
    print(f"Normalized 16 product images into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
