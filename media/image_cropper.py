#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pillow>=10.0.0",
# ]
# ///

from PIL import Image
from pathlib import Path
import sys


OUTPUT_DIR = Path("./separate_samples")

# Increase this if you still see white padding lines.
# Try 8, 10, or 12 if needed.
CROP_INSET = 10


def find_white_runs(values, threshold=245, min_run=3):
    runs = []
    start = None

    for i, value in enumerate(values):
        if value >= threshold:
            if start is None:
                start = i
        else:
            if start is not None:
                if i - start >= min_run:
                    runs.append((start, i - 1))
                start = None

    if start is not None and len(values) - start >= min_run:
        runs.append((start, len(values) - 1))

    return runs


def midpoint(run):
    start, end = run
    return (start + end) // 2


def crop_grid(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        print(f"Skipping missing file: {image_path}")
        return False

    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    col_brightness = []
    for x in range(width):
        total = 0
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            total += (r + g + b) / 3
        col_brightness.append(total / height)

    row_brightness = []
    for y in range(height):
        total = 0
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            total += (r + g + b) / 3
        row_brightness.append(total / width)

    vertical_runs = find_white_runs(col_brightness)
    horizontal_runs = find_white_runs(row_brightness)

    vertical_separators = [
        run for run in vertical_runs
        if run[0] > 5 and run[1] < width - 6
    ]

    horizontal_separators = [
        run for run in horizontal_runs
        if run[0] > 5 and run[1] < height - 6
    ]

    if len(vertical_separators) != 3 or len(horizontal_separators) != 1:
        print(f"Could not confidently detect a 4×2 grid in: {image_path}")
        print(f"Image size: {width}×{height}")
        print(f"Detected vertical separators: {vertical_separators}")
        print(f"Detected horizontal separators: {horizontal_separators}")
        return False

    x_bounds = [0] + [midpoint(run) for run in vertical_separators] + [width]
    y_bounds = [0] + [midpoint(run) for run in horizontal_separators] + [height]

    prefix = image_path.stem
    count = 1

    print(f"\nCropping {image_path}...")

    for row in range(2):
        for col in range(4):
            left = x_bounds[col] + CROP_INSET
            right = x_bounds[col + 1] - CROP_INSET
            top = y_bounds[row] + CROP_INSET
            bottom = y_bounds[row + 1] - CROP_INSET

            if right <= left or bottom <= top:
                print(f"Skipping invalid crop for {image_path}, cell {count}")
                count += 1
                continue

            crop = img.crop((left, top, right, bottom))

            output_path = OUTPUT_DIR / f"{prefix}_stone_{count:02d}.png"
            crop.save(output_path)

            print(f"Saved {output_path}")
            count += 1

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  uv run image_cropper.py input_image_1.png input_image_2.png ...")
        print("")
        print("Example:")
        print("  uv run image_cropper.py stone_samples_8.png stone_samples2_8.png")
        sys.exit(1)

    total = 0
    successful = 0

    for image_path in sys.argv[1:]:
        total += 1
        if crop_grid(image_path):
            successful += 1

    print("")
    print(f"Done. Successfully cropped {successful} of {total} input image(s).")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
