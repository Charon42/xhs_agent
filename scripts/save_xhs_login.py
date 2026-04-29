import asyncio
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import async_playwright

from config import DEFAULT_STORAGE_STATE


async def main() -> None:
    DEFAULT_STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded", timeout=60000)

        print("请在打开的浏览器中手动登录小红书。")
        print("登录完成并确认首页可正常浏览后，回到这个终端按 Enter 保存登录态。")
        input()

        await context.storage_state(path=str(DEFAULT_STORAGE_STATE))
        await browser.close()

    print(f"登录态已保存到: {Path(DEFAULT_STORAGE_STATE).resolve()}")
    print("该文件包含 cookie，请勿提交到 GitHub。项目 .gitignore 已忽略 auth/ 目录。")


if __name__ == "__main__":
    asyncio.run(main())
