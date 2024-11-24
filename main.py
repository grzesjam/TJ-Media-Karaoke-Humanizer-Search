from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import cutlet
from yt_dlp import YoutubeDL
from joblib import Memory

app = FastAPI()
katsu = cutlet.Cutlet()
templates = Jinja2Templates(directory="./ui/")
ydl_opts = {
    'quiet': True,  # Suppress verbose output
    'skip_download': True,  # Don't download video/audio
    'format': 'best',  # Specify format (not used for metadata fetch)
    'default_search': 'auto',  # Search and fetch the first result
}
memory = Memory("./cache", verbose=0)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/search", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="search.html")


@app.get("/api/search")
async def search_json(search: str, type: str, by: str):
    params = {
        "strCond": 0,
        "natType": type,
        "strType": by,
        "strText": search,
        "strSize01": 500
    }
    response = requests.get("https://m.tjmedia.com/tjsong/song_search_result.asp", params=params)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find("div", id="wrap").find("form", {"name": "form"}).find("div", id="BoardType1").findAll("tr")
    songs = []
    # first row is header
    for song in results[1:]:
        id_ = clean_text(song.find("td"))
        if id_ == '검색결과를 찾을수 없습니다.':
            return [{"title": "NOT FOUND"}]
        song_name_element = song.find("td", class_="left")
        song_name = clean_text(song_name_element)
        author_element = song_name_element.find_next_sibling("td")
        author = clean_text(author_element)

        songs.append({
            "id": id_,
            "title": song_name,
            "title_romaji": katsu.romaji(song_name),
            "author": author,
            "author_romaji": katsu.romaji(author),
            "youtube_link": f"https://www.youtube.com/results?search_query={song_name}+{author}",
            "lyrics": f"https://www.google.com/search?q={song_name}+{author}+lyrics",
        })
    return songs


@app.get("/api/song_cover")
async def song_cover(song_name: str):
    # weird way to get cache when using fastapi :shrug:
    @memory.cache
    def get_cover(song_name):
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=False)  # Fetch info without downloading
            try:
                return {"url": info['entries'][0]['thumbnail']}
            except IndexError:
                return None

    return get_cover(song_name)


# helper functions:
def clean_text(element):
    return element.get_text(strip=True) if element else ""
