import argparse
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

PROJECT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = PROJECT_DIR / "images"


def wait_for_page(page: Page, n: int, timeout: int = 8000) -> bool:
    """Wait until #outer_page_{n} exists in the DOM, scrolling down to trigger loading."""
    selector = f"#outer_page_{n}"
    waited = 0
    step = 500
    while waited < timeout:
        if page.locator(selector).count() > 0:
            return True
        page.evaluate(
            "document.querySelector('#pdf_document_scroll_container')"
            "?.scrollTo(0, 1e9); window.scrollTo(0, document.body.scrollHeight)"
        )
        page.wait_for_timeout(step)
        waited += step
    return page.locator(selector).count() > 0


def wait_for_render(page: Page, n: int, timeout: int = 6000) -> None:
    """Wait until the page content (#page{n}) has been rendered and its images are loaded."""
    inner = page.locator(f"#outer_page_{n} #page{n}")
    waited = 0
    while waited < timeout:
        ready = inner.count() > 0 and inner.evaluate(
            """el => el.children.length > 0
                     && [...el.querySelectorAll('img')].every(i => i.complete)"""
        )
        if ready:
            break
        page.wait_for_timeout(250)
        waited += 250
    page.wait_for_timeout(300)


# NEU: komplette Funktion
def hide_overlays(page: Page) -> None:
    """Hide sticky/fixed elements (header, toolbar, banners) that would end up in the screenshot."""
    page.evaluate(
        """() => {
            const doc = document.querySelector('#document_container');
            for (const el of document.querySelectorAll('body *')) {
                if (doc && (doc.contains(el) || el.contains(doc))) continue;
                const pos = getComputedStyle(el).position;
                if (pos === 'fixed' || pos === 'sticky') {
                    el.style.setProperty('display', 'none', 'important');
                }
            }
        }"""
    )


def download_pages(url: str) -> int:
    """Save all document pages as images into IMAGES_DIR. Returns the number of saved pages."""
    IMAGES_DIR.mkdir(exist_ok=True)

    for old in IMAGES_DIR.glob("slide*.jpg"):
        old.unlink()

    saved = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1600, "height": 2000},  # GEÄNDERT: Höhe 1000 -> 2000
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        try:
            page.click("button:has-text('Accept')", timeout=3000)
        except Exception:
            pass

        page.wait_for_selector("div.outer_page")

        n = 1
        while True:
            if not wait_for_page(page, n):
                print(f"No page {n} found, finished downloading.")
                break

            outer = page.locator(f"#outer_page_{n}")
            outer.scroll_into_view_if_needed()
            wait_for_render(page, n)

            hide_overlays(page)            # NEU
            page.wait_for_timeout(100)     # NEU

            try:
                outer.screenshot(
                    path=str(IMAGES_DIR / f"slide{n}.jpg"),
                    type="jpeg",
                    quality=90,
                )
                saved += 1
                print(f"slide{n}.jpg saved")
            except Exception as e:
                print(f"page {n}: screenshot failed ({e})")

            n += 1

        browser.close()

    return saved


# NEU: Alias, damit main.py mit download_slides weiter funktioniert
download_slides = download_pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Save document pages as images")
    parser.add_argument("url", help="URL of the document")
    args = parser.parse_args()

    print(f"Saving to: {IMAGES_DIR}")
    saved = download_pages(args.url)
    print(f"Done. {saved} pages saved.")


if __name__ == "__main__":
    main()
