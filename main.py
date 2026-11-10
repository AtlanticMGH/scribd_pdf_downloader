import argparse
import re
import sys

from make_pdf import PROJECT_DIR, cleanup_images, make_pdf
from scraper import IMAGES_DIR, download_pages


def default_pdf_name(url: str) -> str:
    """Derive a PDF file name from the last part of the URL."""
    name = url.rstrip("/").split("/")[-1].split("?")[0] or "slides"
    return re.sub(r"[^\w\-]", "_", name) + ".pdf"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a SlideShare presentation and convert it to a PDF"
    )
    parser.add_argument("url", help="URL of the SlideShare presentation")
    parser.add_argument(
        "-o", "--output",
        help="Name of the output PDF (default: derived from the URL)",
    )
    parser.add_argument(
        "--keep-images",
        action="store_true",
        help="Do not delete the downloaded images after creating the PDF",
    )
    args = parser.parse_args()

    output_pdf = PROJECT_DIR / (args.output or default_pdf_name(args.url))

    print(f"Saving images to: {IMAGES_DIR}")
    saved = download_pages(args.url)
    if saved == 0:
        sys.exit("No slides could be downloaded.")

    print(f"Downloaded {saved} slides. Creating PDF...")
    make_pdf(output_pdf)
    if not args.keep_images:
        cleanup_images()


if __name__ == "__main__":
    main()
