# 🎬 Multi-Platform Video Scraper API

TikTok + Instagram + YouTube scraper with FastAPI + n8n integration.
No third-party API keys needed!

---

## 🚀 VPS Par Deploy Karna (DigitalOcean / AWS)

### Step 1: Server setup
```bash
apt update && apt install -y docker.io docker-compose git
```

### Step 2: Code upload karo
```bash
git clone <your-repo> /opt/scraper
cd /opt/scraper
```

### Step 3: Start karo
```bash
docker-compose up -d
```

Scraper API: http://YOUR_IP:8000  
n8n Dashboard: http://YOUR_IP:5678  
n8n Login: admin / changeme123

---

## 📡 API Endpoints

### 1. Search Videos
```
POST http://YOUR_IP:8000/api/search
{
  "query": "funny cats",
  "platform": "all",       // tiktok | instagram | youtube | all
  "max_results": 20
}
```

### 2. Profile Videos
```
POST http://YOUR_IP:8000/api/profile
{
  "username": "therock",
  "platform": "instagram",  // tiktok | instagram | youtube
  "max_videos": 30
}
```

### 3. Video Details
```
POST http://YOUR_IP:8000/api/video/details
{
  "url": "https://www.tiktok.com/@user/video/123456"
}
```

### 4. Download Video
```
POST http://YOUR_IP:8000/api/video/download
{
  "url": "https://www.youtube.com/watch?v=abc123",
  "platform": "youtube"
}
```
→ Returns: mp4 file directly

### 5. Duplicate Check
```
GET http://YOUR_IP:8000/api/duplicate/check?video_id=123&platform=tiktok
```

### 6. Stats
```
GET http://YOUR_IP:8000/api/stats
```

---

## 🔗 n8n Se Connect Karna

n8n mein "HTTP Request" node use karo:

### Search Node Setup:
- Method: POST
- URL: `http://scraper:8000/api/search`
- Body (JSON):
```json
{
  "query": "{{ $json.search_term }}",
  "platform": "tiktok",
  "max_results": 20
}
```

### Profile Node Setup:
- Method: POST
- URL: `http://scraper:8000/api/profile`
- Body (JSON):
```json
{
  "username": "{{ $json.username }}",
  "platform": "{{ $json.platform }}",
  "max_videos": 30
}
```

---

## 📊 Response Format (Har Video Ka)

```json
{
  "platform": "youtube",
  "video_id": "abc123",
  "url": "https://youtube.com/watch?v=abc123",
  "title": "Video title",
  "description": "Full description...",
  "channel": "Channel Name",
  "views": 1500000,
  "likes": 45000,
  "comments": 2300,
  "shares": 0,
  "duration": 180,
  "thumbnail": "https://...",
  "hashtags": ["viral", "trending"],
  "upload_date": "20240101",
  "scraped_at": "2024-01-15T10:30:00",
  "is_new": true
}
```

---

## 🛡️ Duplicate Detection

- Har video ka ID track hota hai `data/seen_videos.json` mein
- Same video dobara process nahi hogi
- `is_new: true/false` field se pata chalta hai

---

## ⚙️ Local Testing (Docker ke bina)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API Docs: http://localhost:8000/docs

---

## 📝 Notes

- Instagram ke liye cookies needed ho sakti hain private profiles ke liye
- TikTok rate limiting kar sakta hai — delay add karo agar bahut requests hain
- Videos `downloads/` folder mein save hoti hain
- n8n internal network mein `scraper:8000` use karo (localhost nahi)
