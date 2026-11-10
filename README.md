# slideshare_pdf_downloader

Download all slides of a SlideShare presentation as images and combine them into a single PDF.

## Requirements

- Python 3.8 or newer
- Internet connection

Python packages:

- [playwright](https://playwright.dev/python/) (headless Chromium, needed because slides are lazy-loaded)
- [img2pdf](https://pypi.org/project/img2pdf/) (lossless JPG to PDF conversion)

## Installation

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install the Python packages
pip install playwright img2pdf

# 3. Download the Chromium browser used by Playwright
playwright install chromium

# 4. (Only if Chromium fails to start) install missing system libraries
playwright install-deps chromium
```

## Usage

```bash
# Download slides and create a PDF (name is derived from the URL)
python3 main.py "https://www.slideshare.net/..."

# Custom PDF name
python3 main.py "https://www.slideshare.net/..." -o my_presentation.pdf

# Keep the downloaded images after the PDF has been created
python3 main.py "https://www.slideshare.net/..." --keep-images
```

The PDF is saved in the project folder. By default, the temporary `images/` folder is deleted after the PDF has been created.

### Running the steps separately

```bash
# Only download the slides into ./images
python3 scraper.py "https://www.slideshare.net/..."

# Only create the PDF from the images in ./images
python3 make_pdf.py my_presentation.pdf
```

## Project structure

```
.
├── main.py       # Entry point: download + PDF + cleanup
├── scraper.py    # Downloads the slides (Playwright)
├── make_pdf.py   # Builds the PDF and cleans up the images
└── images/       # Temporary folder (slide1.jpg, slide2.jpg, ...)
```

All three files must be in the same folder.

## How it works

SlideShare loads slides lazily: only the first ~100 slide containers exist in the page at first, and the large images (`...-2048.jpg`) are only loaded when a slide is scrolled into view. The scraper therefore opens the page in a headless browser, scrolls through the slides one by one, waits for each image, and saves it as `slideN.jpg`. Afterwards, `img2pdf` combines the images in numerical order.

## Troubleshooting

- **Fewer slides than expected:** Your connection may be slow. Increase the `timeout` value in `wait_for_slide()` in `scraper.py` (e.g. from `8000` to `15000`).
- **`Executable doesn't exist` error:** Run `playwright install chromium` again inside the activated virtual environment.
- **Chromium fails to start / missing libraries:** Run `playwright install-deps chromium`.
- **No slides found:** SlideShare may have changed its page structure. Check the selectors (`div.slide-item`, `#slideN`, `img[data-testid='vertical-slide-image']`) in `scraper.py`.
- **"Warning: missing slides":** Some images failed to download. Run the script again.

## Disclaimer

Only download presentations you are allowed to copy. Respect the copyright of the authors and SlideShare's terms of service.
