import argparse
import asyncio
import os
import sys
import logging
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

import aiohttp
from tqdm.asyncio import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("boosty-milker")

class BoostyClient:
    API_URL = "https://api.boosty.to/v1/blog/{}/post/"
    
    def __init__(self, session: aiohttp.ClientSession, auth_token: Optional[str] = None):
        self.session = session
        self.auth_token = auth_token
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://boosty.to",
            "Referer": "https://boosty.to/"
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    async def get_posts(self, blog_name: str, limit: int = 100, offset: str = "") -> Dict[str, Any]:
        url = self.API_URL.format(blog_name)
        params = {
            "limit": limit,
            "comments_limit": 0,
            "reply_limit": 0,
        }
        if offset:
            params["offset"] = offset

        async with self.session.get(url, params=params, headers=self.headers) as resp:
            if resp.status == 401:
                logger.error(f"{Fore.RED}Unauthorized. Please provide a valid auth token for private content.")
                return {}
            if resp.status == 403:
                logger.error(f"{Fore.RED}Access denied. Check your token or subscription.")
                return {}
            if resp.status != 200:
                logger.error(f"{Fore.RED}Error fetching posts: {resp.status}")
                return {}
            return await resp.json()

class Downloader:
    def __init__(self, download_dir: Path, max_concurrency: int = 5):
        self.download_dir = download_dir
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_file(self, session: aiohttp.ClientSession, url: str, filename: str) -> bool:
        filepath = self.download_dir / filename
        
        # Simple sanitization
        filepath = Path(str(filepath).split("?")[0]) # Remove query params from filename if present
        
        if filepath.exists():
            return True # Skip existing

        async with self.semaphore:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(filepath, "wb") as f:
                            f.write(content)
                        return True
                    else:
                        logger.warning(f"Failed to download {url}: {resp.status}")
                        return False
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                return False

async def process_post(post: Dict[str, Any], downloader: Downloader, session: aiohttp.ClientSession, tasks: List[Any]):
    post_id = post.get("id")
    title = post.get("title", "")
    published = post.get("publishTime", 0)
    date_str = datetime.fromtimestamp(published).strftime('%Y-%m-%d')
    
    # Process data blocks
    data_blocks = post.get("data", [])
    if not data_blocks:
        return

    img_count = 0
    for block in data_blocks:
        block_type = block.get("type")
        url = None
        
        if block_type == "image":
            url = block.get("url")
            # Sometimes URL is inside 'content'
            if not url and "content" in block:
                # content might be a string (unlikely for image) or object
                pass 
            
            # High quality URL is usually main URL
        
        # Handle teaser blocks for locked posts if visible
        if block_type == "teaser_image":
             pass # Usually blurred, skip

        if url:
            img_count += 1
            filename = f"{date_str}_post{post_id}_{img_count}.jpg"
            tasks.append(downloader.download_file(session, url, filename))

    # Boosty structure varies; sometimes 'teaser' contains images if locked but we have access? 
    # Usually 'data' contains the content we can see.

async def async_main():
    parser = argparse.ArgumentParser(description="Boosty Milker - Photo Downloader")
    parser.add_argument("--username", required=True, help="Boosty creator username")
    parser.add_argument("--directory", required=True, help="Directory to save photos")
    parser.add_argument("--auth_token", help="Bearer token for private content", default=None)
    parser.add_argument("--max_concurrency", type=int, default=10, help="Max concurrent downloads")
    
    args = parser.parse_args()
    
    auth_token = args.auth_token
    if not auth_token:
        # Check env var
        auth_token = os.environ.get("BOOSTY_TOKEN")

    async with aiohttp.ClientSession() as session:
        client = BoostyClient(session, auth_token)
        downloader = Downloader(Path(args.directory), args.max_concurrency)
        
        logger.info(f"{Fore.CYAN}Starting download for user: {args.username}")
        if auth_token:
            logger.info(f"{Fore.GREEN}Authenticated with token.")
        
        offset = ""
        tasks = []
        total_posts = 0
        
        pbar_posts = tqdm(desc="Fetching posts", unit="page")
        
        while True:
            data = await client.get_posts(args.username, offset=offset)
            if not data or "data" not in data:
                break
                
            posts = data["data"]
            if not posts:
                break
                
            for post in posts:
                process_post_sync(post, tasks, downloader, session)
            
            total_posts += len(posts)
            pbar_posts.update(1)
            
            extra = data.get("extra", {})
            offset = extra.get("offset")
            if not offset:
                break
        
        pbar_posts.close()
        logger.info(f"Found {len(tasks)} images in {total_posts} posts.")
        
        if tasks:
            results = await tqdm.gather(*tasks, desc="Downloading images", unit="img")
            success_count = sum(results)
            logger.info(f"{Fore.GREEN}Downloaded {success_count}/{len(tasks)} images.")
        else:
            logger.info("No images found.")

def process_post_sync(post, tasks, downloader, session):
    """Synchronous helper to extract URLs and add tasks"""
    post_id = post.get("id")
    published = post.get("publishTime", 0)
    date_str = datetime.fromtimestamp(published).strftime('%Y-%m-%d')
    
    data_blocks = post.get("data", [])
    if not data_blocks:
        return

    img_count = 0
    for block in data_blocks:
        if block.get("type") == "image":
            url = block.get("url")
            # Try to get max resolution
            # The 'url' field is usually the full size or decent size. 
            # Sometimes there are 'resolutions' or 'urls' map?
            # Boosty API 'image' block usually has 'url' at top level.
            
            if url:
                img_count += 1
                # Clean URL
                if "?" in url:
                    clean_url = url # Keep params for download if signed, but filename needs clean ext
                
                # Deduce extension
                ext = ".jpg"
                if ".png" in url.lower(): ext = ".png"
                elif ".webp" in url.lower(): ext = ".webp"
                
                filename = f"{date_str}_{post_id}_img{img_count}{ext}"
                tasks.append(downloader.download_file(session, url, filename))

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
