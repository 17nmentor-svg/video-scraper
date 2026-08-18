import json
import os
from datetime import datetime

DB_FILE = "data/seen_videos.json"


class DuplicateChecker:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.db = self._load()

    def _load(self) -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(DB_FILE, "w") as f:
            json.dump(self.db, f, indent=2)

    def _key(self, video_id: str, platform: str) -> str:
        return f"{platform}:{video_id}"

    def is_duplicate(self, video_id: str, platform: str) -> bool:
        return self._key(video_id, platform) in self.db

    def mark_seen(self, video_id: str, platform: str):
        key = self._key(video_id, platform)
        self.db[key] = {"seen_at": datetime.utcnow().isoformat(), "platform": platform}
        self._save()

    def get_stats(self) -> dict:
        stats = {"total": len(self.db), "by_platform": {}}
        for key, val in self.db.items():
            p = val.get("platform", "unknown")
            stats["by_platform"][p] = stats["by_platform"].get(p, 0) + 1
        return stats

    def reset(self):
        self.db = {}
        self._save()
