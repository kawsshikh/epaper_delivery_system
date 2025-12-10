import asyncio
from playwright.async_api import async_playwright
from typing import Optional, List
import re


class EpaperScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def _scrape(self, url: str, timeout: int = 50000) -> Optional[str]:
        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )

                context = await browser.new_context(
                    permissions=['camera', 'microphone', 'notifications'],
                    geolocation={"latitude": 0, "longitude": 0},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = await context.new_page()
                await page.goto(url, timeout=timeout)
                html_content = await page.content()
                return html_content

            except Exception as e:
                print(f"Erroring scraping {url} {e}")
                return None

            finally:
                if browser:
                    await browser.close()

    def scrape(self, url: str) -> Optional[str]:
        html_content = asyncio.run(self._scrape(url))
        return html_content

def gather_imgs(url: str) -> Optional[List[str]]:
    scraper = EpaperScraper()
    html_content = scraper.scrape(url)

    if html_content:
        pattern = r'highres="([^"]*hr)\.jpg"'
        images_urls = re.findall(pattern, html_content)

        unique_images_urls = []
        for image_url in images_urls:
            if image_url not in unique_images_urls:
                unique_images_urls.append(image_url)

        return unique_images_urls
    return None


def main():
    url = "https://epaper.eenadu.net/Home/Index?date=09/12/2025&eid=2"
    urls = gather_imgs(url)
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()