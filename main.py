from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from app.scraper import MultiPlatformScraper
from app.duplicate_checker import DuplicateChecker
import os

app = FastAPI(
    title="Multi-Platform Video Scraper API",
    description="TikTok, Instagram, YouTube scraper with n8n support",
    version="1.0.0"
)

scraper = MultiPlatformScraper()
dup_checker = DuplicateChecker()

# ─── Models ───────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    platform: str = "all"       # tiktok | instagram | youtube | all
    max_results: int = 20

class ProfileRequest(BaseModel):
    username: str
    platform: str               # tiktok | instagram | youtube
    max_videos: int = 30

class VideoDetailRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    platform: str

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "running", "message": "Multi-Platform Video Scraper API"}

@app.get("/health")
def health():
    return {"status": "ok"}

# 1. Search videos
@app.post("/api/search")
async def search_videos(req: SearchRequest):
    try:
        platforms = ["tiktok", "instagram", "youtube"] if req.platform == "all" else [req.platform]
        all_results = []

        for platform in platforms:
            results = await scraper.search(platform, req.query, req.max_results)
            for video in results:
                if not dup_checker.is_duplicate(video["video_id"], platform):
                    dup_checker.mark_seen(video["video_id"], platform)
                    video["is_new"] = True
                else:
                    video["is_new"] = False
                all_results.append(video)

        return {"success": True, "count": len(all_results), "results": all_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Profile videos
@app.post("/api/profile")
async def profile_videos(req: ProfileRequest):
    try:
        results = await scraper.get_profile_videos(req.platform, req.username, req.max_videos)
        new_count = 0
        for video in results:
            if not dup_checker.is_duplicate(video["video_id"], req.platform):
                dup_checker.mark_seen(video["video_id"], req.platform)
                video["is_new"] = True
                new_count += 1
            else:
                video["is_new"] = False

        return {"success": True, "username": req.username, "platform": req.platform,
                "total": len(results), "new": new_count, "videos": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Video details
@app.post("/api/video/details")
async def video_details(req: VideoDetailRequest):
    try:
        details = await scraper.get_video_details(req.url)
        return {"success": True, "data": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Download video
@app.post("/api/video/download")
async def download_video(req: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        file_path = await scraper.download_video(req.url, req.platform)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Download failed")
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            filename=os.path.basename(file_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Duplicate check
@app.get("/api/duplicate/check")
def check_duplicate(video_id: str, platform: str):
    is_dup = dup_checker.is_duplicate(video_id, platform)
    return {"video_id": video_id, "platform": platform, "is_duplicate": is_dup}

# 6. Stats
@app.get("/api/stats")
def get_stats():
    return dup_checker.get_stats()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
