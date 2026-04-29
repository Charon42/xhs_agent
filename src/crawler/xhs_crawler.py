import asyncio
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

from src.utils.logger import get_logger


logger = get_logger(__name__)


class XHSCrawler:
    """Compliant Playwright crawler for logged-in personal learning tests.

    This crawler does not bypass login, captcha, rate limits, or anti-bot controls.
    Save your own login state first with scripts/save_xhs_login.py, then run live mode.
    """

    def __init__(self, storage_state_path: Path, headless: bool = True) -> None:
        self.storage_state_path = storage_state_path
        self.headless = headless

    def fetch_notes(self, keyword: str, limit: int = 5) -> list[dict[str, Any]]:
        return asyncio.run(self._fetch_notes(keyword=keyword, limit=limit))

    async def _fetch_notes(self, keyword: str, limit: int) -> list[dict[str, Any]]:
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright is not installed. Run: pip install -r requirements.txt") from exc

        if not self.storage_state_path.exists():
            raise FileNotFoundError(
                f"Login state not found: {self.storage_state_path}. "
                "Run: python scripts/save_xhs_login.py"
            )

        notes: list[dict[str, Any]] = []
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}"
        logger.info("Opening XHS search page: %s", search_url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(storage_state=str(self.storage_state_path))
            page = await context.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)

            for _ in range(4):
                await page.mouse.wheel(0, 1200)
                await page.wait_for_timeout(1200)

            links = await self._extract_note_links(page, limit)
            if not links:
                await browser.close()
                raise RuntimeError(
                    "No note links found. Check whether the saved login state is still valid, "
                    "the page loaded normally, and the keyword has search results."
                )

            for url in links[:limit]:
                try:
                    note = await self._extract_note_detail(context, url)
                    notes.append(note)
                    logger.info("Fetched note: %s", note["title"])
                except PlaywrightTimeoutError:
                    logger.warning("Timed out while fetching note: %s", url)
                except Exception as exc:
                    logger.warning("Failed to fetch note %s: %s", url, exc)

            await browser.close()

        return notes

    async def _extract_note_links(self, page: Any, limit: int) -> list[str]:
        hrefs = await page.locator("a[href*='/explore/']").evaluate_all(
            "(els) => els.map((el) => el.href).filter(Boolean)"
        )

        links: list[str] = []
        for href in hrefs:
            clean_url = str(href).split("?")[0]
            if clean_url not in links:
                links.append(clean_url)
            if len(links) >= limit:
                break
        return links

    async def _extract_note_detail(self, context: Any, url: str) -> dict[str, Any]:
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(2500)

        title = await self._first_text(
            page,
            [
                "#detail-title",
                ".note-content .title",
                "[class*='title']",
                "meta[property='og:title']",
                "title",
            ],
        )
        content = await self._first_text(
            page,
            [
                "#detail-desc",
                ".note-content .desc",
                "[class*='desc']",
                "meta[name='description']",
            ],
        )
        body_text = await page.locator("body").inner_text(timeout=10000)
        if not title:
            title = (await page.title()).replace(" - 小红书", "").strip()
        if not content:
            content = self._fallback_content(body_text, title)

        tags = self._extract_tags(body_text)
        likes = self._extract_metric(body_text, ["点赞", "赞"])
        collects = self._extract_metric(body_text, ["收藏"])
        comments = self._extract_metric(body_text, ["评论"])
        author = await self._first_text(page, [".username", "[class*='author']", "[class*='user']"])

        await page.close()
        return {
            "title": title,
            "content": content,
            "tags": tags,
            "likes": likes,
            "collects": collects,
            "comments": comments,
            "url": url,
            "author": author or "",
            "published_at": "",
        }

    async def _first_text(self, page: Any, selectors: list[str]) -> str:
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                if await locator.count() == 0:
                    continue
                if selector.startswith("meta"):
                    value = await locator.get_attribute("content", timeout=2000)
                else:
                    value = await locator.inner_text(timeout=2000)
                value = (value or "").strip()
                if value:
                    return value
            except Exception:
                continue
        return ""

    def _fallback_content(self, body_text: str, title: str) -> str:
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        filtered = [line for line in lines if line != title and len(line) > 10]
        return "\n".join(filtered[:8])

    def _extract_tags(self, text: str) -> list[str]:
        tags = []
        for tag in re.findall(r"#([\w\u4e00-\u9fff-]+)", text):
            if tag not in tags:
                tags.append(tag)
        return tags[:8]

    def _extract_metric(self, text: str, labels: list[str]) -> str:
        for label in labels:
            match = re.search(rf"([\d.,]+[万wkK]?)\s*{label}", text)
            if match:
                return match.group(1)
        return "0"
