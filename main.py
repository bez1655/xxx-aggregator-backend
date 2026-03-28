from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import torch
import torch.nn as nn
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

# 50+ сайтов (можно расширять)
SITES = [
    "https://www.pornhub.com", "https://www.xvideos.com", "https://xhamster.com",
    "https://www.youporn.com", "https://www.redtube.com", "https://spankbang.com",
    "https://www.eporner.com", "https://www.xnxx.com", "https://www.porntrex.com",
    # Добавляй остальные по мере необходимости
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
        r = requests.get(f"{site}/search?search={query}", timeout=8, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        videos = []
        for item in soup.select("div.videoItem, li.video, div.thumb, .video-card")[:8]:
            title_tag = item.select_one("a.title, span.title, img[alt], .title")
            thumb_tag = item.select_one("img")
            link_tag = item.select_one("a")
            title = (title_tag.text.strip() if title_tag and hasattr(title_tag, "text") else "Untitled Video")
            thumb = thumb_tag["src"] if thumb_tag and "src" in thumb_tag.attrs else ""
            link = link_tag["href"] if link_tag else ""
            videos.append({
                "title": title[:80],
                "thumb": thumb if thumb.startswith("http") else f"{site}{thumb}",
                "url": f"{site}{link}" if link and not link.startswith("http") else link or "",
                "duration": "10:00",
                "id": str(random.randint(10000, 99999))
            })
        return videos
    except Exception as e:
        print(f"Scrape error {site}: {e}")
        return []

@app.get("/api/videos")
async def get_videos(query: str = Query("hot")):
    all_videos = []
    for site in SITES[:12]:   # лимит, чтобы не убить время билда
        all_videos.extend(scrape_site(site, query))
    return {"videos": all_videos[:120], "total": len(all_videos), "source": "scraped"}

# Простой AI-рекомендер (Torch)
class SimpleRecommender(nn.Module):
    def __init__(self):
        super().__init__()
        self.dummy = nn.Parameter(torch.randn(1))

    def forward(self, x):
        return torch.sigmoid(x)

model = SimpleRecommender()

@app.post("/api/recommend")
async def recommend(user_history: List[str] = []):
    # Заглушка — в будущем обучай на реальных просмотрах
    recommended = [{"id": vid, "title": f"AI Рекомендация {i}", "score": 0.92 - i*0.02} for i, vid in enumerate(user_history[-15:])]
    return {"recommendations": recommended or [{"id": "demo", "title": "Популярное сейчас (AI Torch)", "score": 0.95}]}

@app.get("/health")
async def health():
    return {"status": "ok", "python": "3.14", "torch_available": torch.__version__}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)8000)
