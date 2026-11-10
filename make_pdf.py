import re
import sys
from pathlib import Path

import img2pdf

PROJECT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = PROJECT_DIR / "images"


def slide_number(path: Path) -> int:
    """Extract the number from 'slideX.jpg' to get the correct order."""
    match = re.search(r"slide(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def make_pdf(output_pdf: Path) -> None:
    """Combine all downloaded images into a single PDF, ordered by slide number."""
    files = sorted(IMAGES_DIR.glob("slide*.jpg"), key=slide_number)
    if not files:
        sys.exit(f"No images found in {IMAGES_DIR}.")

    print(f"{len(files)} images found: {files[0].name} to {files[-1].name}")

    # Report gaps in the numbering (e.g. if a download failed)
    numbers = [slide_number(f) for f in files]
    missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
    if missing:
        print(f"Warning: missing slides: {missing}")

    with open(output_pdf, "wb") as f:
        img2pdf.convert([str(p) for p in files], outputstream=f)

    print(f"PDF created: {output_pdf}")


def cleanup_images() -> None:
    """Delete the downloaded images and the images folder if it is empty."""
    for img in IMAGES_DIR.glob("slide*.jpg"):
        img.unlink()
    try:
        IMAGES_DIR.rmdir()  # only succeeds if the folder is empty
    except OSError:
        pass
    print(f"Deleted temporary images in {IMAGES_DIR}")


def main() -> None:
    output_pdf = PROJECT_DIR / (sys.argv[1] if len(sys.argv) > 1 else "slides.pdf")
    make_pdf(output_pdf)


if __name__ == "__main__":
    main()