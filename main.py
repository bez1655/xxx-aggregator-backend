from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import random
from pydantic import BaseModel

app = FastAPI(title="XXXAggregator Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SITES = [
    "https://www.pornhub.com", "https://www.xvideos.com", "https://xhamster.com",
    "https://www.youporn.com", "https://spankbang.com", "https://www.eporner.com",
    "https://www.xnxx.com", "https://www.porntrex.com",
]

class Video(BaseModel):
    id: str
    title: str
    thumb: str
    url: str
    duration: str
    is_vr: bool = False

def scrape_site(site: str, query: str = "hot") -> List[Dict]:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; XXXAggregator/1.0)"}
        r = requests.get(f"{site}/search?search={query}", timeout=10, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        videos = []
        for item in soup.select("div.videoItem, li.video, div.thumb, .video-card, article")[:10]:
            title_tag = item.select_one("a.title, span.title, .title, img[alt]")
            thumb_tag = item.select_one("img")
            link_tag = item.select_one("a[href]")
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"
            thumb = thumb_tag.get("src", "") if thumb_tag else ""
            link = link_tag.get("href", "") if link_tag else ""
            videos.append({
                "title": title[:100],
                "thumb": thumb if thumb.startswith("http") else f"{site}{thumb}",
                "url": f"{site}{link}" if link and not link.startswith("http") else link,
                "duration": "10:00",
                "id": str(random.randint(10000, 99999))
            })
        return [v for v in videos if v.get("thumb")]
    except:
        return []

@app.get("/api/videos")
async def get_videos(query: str = Query("hot")):
    all_videos = []
    for site in SITES:
        all_videos.extend(scrape_site(site, query))
    return {"videos": all_videos[:120], "total": len(all_videos)}

@app.post("/api/recommend")
async def recommend(user_history: List[str] = []):
    recs = [{"id": vid or f"rec_{i}", "title": f"AI Рекомендация {i+1} 🔥", "score": round(0.98 - i*0.03, 2)} 
            for i, vid in enumerate(user_history[-12:])]
    return {"recommendations": recs or [{"id": "demo", "title": "Популярное сейчас", "score": 0.95}]}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "XXX Aggregator Backend готов!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
