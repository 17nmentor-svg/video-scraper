import asyncio
import re
import os
import httpx
import yt_dlp
from typing import List, Dict, Optional
from datetime import datetime

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class MultiPlatformScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    # ─── Search ───────────────────────────────────────────────────────────────

    async def search(self, platform: str, query: str, max_results: int) -> List[Dict]:
        if platform == "tiktok":
            return await self._search_tiktok(query, max_results)
        elif platform == "instagram":
            return await self._search_instagram(query, max_results)
        elif platform == "youtube":
            return await self._search_youtube(query, max_results)
        return []

    async def _search_tiktok(self, query: str, max_results: int) -> List[Dict]:
        """Search TikTok via web scraping (no API key needed)"""
        results = []
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "playlistend": max_results,
            }
            search_url = f"ytsearch{max_results}:{query} site:tiktok.com"
            # Use yt-dlp TikTok search
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self._ydl_extract(
                f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}", ydl_opts
            ))
            if data:
                entries = data.get("entries", [data])
                for entry in entries[:max_results]:
                    results.append(self._normalize_tiktok(entry))
        except Exception as e:
            print(f"TikTok search error: {e}")
        return [r for r in results if r]

    async def _search_youtube(self, query: str, max_results: int) -> List[Dict]:
        results = []
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "playlistend": max_results,
            }
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self._ydl_extract(
                f"ytsearch{max_results}:{query}", ydl_opts
            ))
            if data:
                for entry in data.get("entries", [])[:max_results]:
                    results.append(self._normalize_youtube(entry))
        except Exception as e:
            print(f"YouTube search error: {e}")
        return [r for r in results if r]

    async def _search_instagram(self, query: str, max_results: int) -> List[Dict]:
        """Instagram hashtag search"""
        results = []
        try:
            tag = query.strip().replace(" ", "").replace("#", "")
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "playlistend": max_results,
            }
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self._ydl_extract(
                f"https://www.instagram.com/explore/tags/{tag}/", ydl_opts
            ))
            if data:
                for entry in data.get("entries", [])[:max_results]:
                    results.append(self._normalize_instagram(entry))
        except Exception as e:
            print(f"Instagram search error: {e}")
        return [r for r in results if r]

    # ─── Profile Videos ───────────────────────────────────────────────────────

    async def get_profile_videos(self, platform: str, username: str, max_videos: int) -> List[Dict]:
        username = username.lstrip("@")
        url_map = {
            "tiktok": f"https://www.tiktok.com/@{username}",
            "instagram": f"https://www.instagram.com/{username}/",
            "youtube": f"https://www.youtube.com/@{username}/videos",
        }
        url = url_map.get(platform)
        if not url:
            return []

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "playlistend": max_videos,
        }
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self._ydl_extract(url, ydl_opts))
        if not data:
            return []

        normalizers = {
            "tiktok": self._normalize_tiktok,
            "instagram": self._normalize_instagram,
            "youtube": self._normalize_youtube,
        }
        norm = normalizers.get(platform, lambda x: x)
        results = []
        for entry in data.get("entries", [data])[:max_videos]:
            r = norm(entry)
            if r:
                results.append(r)
        return results

    # ─── Video Details ─────────────────────────────────────────────────────────

    async def get_video_details(self, url: str) -> Dict:
        ydl_opts = {"quiet": True, "no_warnings": True}
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self._ydl_extract(url, ydl_opts))
        if not data:
            raise ValueError("Could not extract video details")

        platform = self._detect_platform(url)
        if platform == "youtube":
            return self._normalize_youtube(data)
        elif platform == "instagram":
            return self._normalize_instagram(data)
        else:
            return self._normalize_tiktok(data)

    # ─── Download ─────────────────────────────────────────────────────────────

    async def download_video(self, url: str, platform: str) -> Optional[str]:
        video_id = self._extract_id_from_url(url)
        out_path = os.path.join(DOWNLOAD_DIR, f"{platform}_{video_id}.mp4")

        if os.path.exists(out_path):
            return out_path  # already downloaded

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": out_path,
            "format": "best[ext=mp4]/best",
            "merge_output_format": "mp4",
        }

        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, lambda: self._ydl_download(url, ydl_opts))
        return out_path if success and os.path.exists(out_path) else None

    # ─── yt-dlp helpers ───────────────────────────────────────────────────────

    def _ydl_extract(self, url: str, opts: dict) -> Optional[Dict]:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"yt-dlp extract error: {e}")
            return None

    def _ydl_download(self, url: str, opts: dict) -> bool:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"yt-dlp download error: {e}")
            return False

    # ─── Normalizers ──────────────────────────────────────────────────────────

    def _normalize_youtube(self, e: Dict) -> Optional[Dict]:
        if not e:
            return None
        vid_id = e.get("id") or e.get("display_id") or ""
        return {
            "platform": "youtube",
            "video_id": vid_id,
            "url": e.get("webpage_url") or f"https://youtube.com/watch?v={vid_id}",
            "title": e.get("title", ""),
            "description": e.get("description", ""),
            "channel": e.get("uploader") or e.get("channel", ""),
            "views": e.get("view_count", 0),
            "likes": e.get("like_count", 0),
            "comments": e.get("comment_count", 0),
            "shares": 0,
            "duration": e.get("duration", 0),
            "thumbnail": e.get("thumbnail", ""),
            "hashtags": self._extract_hashtags(e.get("description", "") + " " + e.get("title", "")),
            "upload_date": e.get("upload_date", ""),
            "scraped_at": datetime.utcnow().isoformat(),
        }

    def _normalize_tiktok(self, e: Dict) -> Optional[Dict]:
        if not e:
            return None
        vid_id = e.get("id") or e.get("display_id") or ""
        desc = e.get("description") or e.get("title") or ""
        return {
            "platform": "tiktok",
            "video_id": vid_id,
            "url": e.get("webpage_url") or e.get("url") or "",
            "title": desc[:100],
            "description": desc,
            "channel": e.get("uploader") or e.get("creator", ""),
            "views": e.get("view_count", 0),
            "likes": e.get("like_count", 0),
            "comments": e.get("comment_count", 0),
            "shares": e.get("repost_count", 0),
            "duration": e.get("duration", 0),
            "thumbnail": e.get("thumbnail", ""),
            "hashtags": self._extract_hashtags(desc),
            "upload_date": e.get("upload_date", ""),
            "scraped_at": datetime.utcnow().isoformat(),
        }

    def _normalize_instagram(self, e: Dict) -> Optional[Dict]:
        if not e:
            return None
        vid_id = e.get("id") or e.get("display_id") or ""
        desc = e.get("description") or e.get("title") or ""
        return {
            "platform": "instagram",
            "video_id": vid_id,
            "url": e.get("webpage_url") or e.get("url") or "",
            "title": desc[:100],
            "description": desc,
            "channel": e.get("uploader") or e.get("channel", ""),
            "views": e.get("view_count", 0),
            "likes": e.get("like_count", 0),
            "comments": e.get("comment_count", 0),
            "shares": 0,
            "duration": e.get("duration", 0),
            "thumbnail": e.get("thumbnail", ""),
            "hashtags": self._extract_hashtags(desc),
            "upload_date": e.get("upload_date", ""),
            "scraped_at": datetime.utcnow().isoformat(),
        }

    # ─── Utilities ────────────────────────────────────────────────────────────

    def _extract_hashtags(self, text: str) -> List[str]:
        return list(set(re.findall(r"#(\w+)", text or "")))

    def _detect_platform(self, url: str) -> str:
        if "tiktok" in url:
            return "tiktok"
        elif "instagram" in url:
            return "instagram"
        elif "youtube" in url or "youtu.be" in url:
            return "youtube"
        return "unknown"

    def _extract_id_from_url(self, url: str) -> str:
        patterns = [
            r"tiktok\.com/@[^/]+/video/(\d+)",
            r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)",
            r"youtube\.com/watch\?v=([A-Za-z0-9_-]+)",
            r"youtu\.be/([A-Za-z0-9_-]+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, url)
            if m:
                return m.group(1)
        return url[-20:].replace("/", "_")
