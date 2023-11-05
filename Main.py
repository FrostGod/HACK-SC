from fastapi import FastAPI, Path, Query
from pytube import YouTube

import yt_dlp

app = FastAPI()

@app.get('/')
def home():
    return {"Data: Test"}


@app.post('/upload')
async def upload_video(url: str):
    Down(url)
    return {"Data": url}

# https://youtu.be/2lAe1cqCOXo
def Down(url):
    "put it here"
    URL = url

    ydl_opts = {
        "writesubtitles": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])

    print(ydl)


    # YouTube(url).streams.first().download()
    # yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
    # yt.streams

