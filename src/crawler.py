"""Web crawler for deeplearning.ai The Batch articles using Scrapy + Playwright."""

import json
import re
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod


BASE_URL = "https://www.deeplearning.ai"
LETTERS_URL = f"{BASE_URL}/the-batch/tag/letters/"
DATA_DIR = Path(__file__).parent.parent / "data" / "input" / "articles"


class BatchLettersSpider(scrapy.Spider):
    """Spider to crawl The Batch newsletter articles."""

    name = "batch_letters"

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {"processed": 0, "skipped": 0, "failed": 0}

    def start_requests(self):
        """Start crawling from the letters listing page."""
        yield scrapy.Request(
            url=LETTERS_URL,
            callback=self.parse_listing,
            meta={"playwright": True},
        )

    def parse_listing(self, response):
        """Parse the listing page to extract article URLs and pagination."""
        next_data_script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        if next_data_script:
            try:
                data = json.loads(next_data_script)
                posts = data.get("props", {}).get("pageProps", {}).get("posts", [])
                total_pages = data.get("props", {}).get("pageProps", {}).get("totalPages", 1)

                self.logger.info(f"Found {len(posts)} posts on this page, {total_pages} total pages")

                for post in posts:
                    slug = post.get("slug")
                    title = post.get("title")
                    published_at = post.get("published_at")

                    if slug:
                        article_url = f"{BASE_URL}/the-batch/{slug}/"
                        article_dir = self.data_dir / slug

                        # Check if already downloaded (incremental crawl)
                        text_file = article_dir / "article.txt"
                        if text_file.exists():
                            self.logger.info(f"Skipping already downloaded: {slug}")
                            self.stats["skipped"] += 1
                            continue

                        yield scrapy.Request(
                            url=article_url,
                            callback=self.parse_article,
                            meta={
                                "playwright": True,
                                "playwright_include_page": True,
                                "playwright_page_methods": [
                                    PageMethod("wait_for_load_state", "networkidle"),
                                ],
                                "slug": slug,
                                "title": title,
                                "published_at": published_at,
                            },
                        )

                # Handle pagination
                current_page = response.meta.get("page", 1)
                if current_page < total_pages:
                    next_page = current_page + 1
                    next_url = f"{LETTERS_URL}page/{next_page}/"
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse_listing,
                        meta={"playwright": True, "page": next_page},
                    )

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse __NEXT_DATA__: {e}")

    async def parse_article(self, response):
        """Parse an individual article page to extract text."""
        slug = response.meta["slug"]
        title = response.meta["title"]
        published_at = response.meta["published_at"]
        page = response.meta.get("playwright_page")

        self.logger.info(f"Processing article: {title} ({slug})")

        article_dir = self.data_dir / slug
        article_dir.mkdir(parents=True, exist_ok=True)

        # Extract article content from __NEXT_DATA__
        next_data_script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        article_text = ""

        if next_data_script:
            try:
                data = json.loads(next_data_script)
                post = data.get("props", {}).get("pageProps", {}).get("post", {})
                html_content = post.get("html", "")

                article_text = self._extract_text_from_html(html_content)

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse article JSON: {e}")

        # Fallback: extract text from rendered page
        if not article_text:
            paragraphs = response.xpath('//article//p//text()').getall()
            article_text = "\n\n".join(p.strip() for p in paragraphs if p.strip())

        if page:
            await page.close()

        # Save article metadata
        metadata = {
            "slug": slug,
            "title": title,
            "published_at": published_at,
            "url": response.url,
        }

        metadata_file = article_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Save article text
        if article_text:
            text_file = article_dir / "article.txt"
            full_text = f"# {title}\n\nPublished: {published_at}\nURL: {response.url}\n\n---\n\n{article_text}"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(full_text)
            self.logger.info(f"Saved article text: {text_file}")
        else:
            self.logger.warning(f"No article text found for: {slug}")

        self.stats["processed"] += 1

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content."""
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Replace block elements with newlines
        html_content = re.sub(r'</?(p|div|br|h[1-6]|li|tr)[^>]*>', '\n', html_content, flags=re.IGNORECASE)

        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)

        # Decode HTML entities
        html_content = html_content.replace('&nbsp;', ' ')
        html_content = html_content.replace('&amp;', '&')
        html_content = html_content.replace('&lt;', '<')
        html_content = html_content.replace('&gt;', '>')
        html_content = html_content.replace('&quot;', '"')
        html_content = html_content.replace('&#39;', "'")

        # Clean up whitespace
        lines = [line.strip() for line in html_content.split('\n')]
        lines = [line for line in lines if line]

        return '\n\n'.join(lines)

    def closed(self, reason):
        """Log final statistics when spider closes."""
        self.logger.info(
            f"Crawl finished. Processed: {self.stats['processed']}, "
            f"Skipped: {self.stats['skipped']}, Failed: {self.stats['failed']}"
        )


def run_crawler():
    """Run the crawler."""
    process = CrawlerProcess()
    process.crawl(BatchLettersSpider)
    process.start()


if __name__ == "__main__":
    run_crawler()
