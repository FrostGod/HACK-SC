from fastapi import FastAPI
import os
import yt_dlp
import webvtt
from yt_dlp import YoutubeDL

app = FastAPI()


@app.get("/")
def home():
    return {"Data: Test"}


@app.post("/upload")
async def upload_video(url: str):
    return {"Data": "hello"}


@app.post("/get_subtitles")
async def get_subtitles(url: str):
    data = extract_subtitles(url)
    return {"Data": data}


def get_video_metadata(ydl: YoutubeDL, url: str):
    info_dict = ydl.extract_info(url, download=False)
    return info_dict


def exist_subtitles(info_dict):
    subtitles = info_dict["subtitles"]
    automatic_captions = info_dict["automatic_captions"]
    return subtitles or automatic_captions


def extract_subtitles_from_vtt(vtt_file_str):
    vtt = webvtt.read(vtt_file_str)
    starts = []
    ends = []
    caption_texts = []

    for caption in vtt:
        starts.append(caption.start)
        ends.append(caption.end)
        caption_text = caption.text.strip().replace("\n", " ")
        caption_texts.append(caption_text)
    return {
        "starts": starts,
        "ends": ends,
        "caption_texts": caption_texts,
    }


def extract_subtitles(url: str):
    tmp_file_str = "tmp"
    ydl_opts = {
        "writesubtitles": True,
        "skip_download": True,
        "outtmpl": tmp_file_str,
        "writeautomaticsub": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not exist_subtitles(get_video_metadata(ydl, url)):
                raise Exception("No subtitles found")
            ydl.download([url])
        vtt_file_str = tmp_file_str + ".en.vtt"
        subtitle_dict = extract_subtitles_from_vtt(vtt_file_str)
        return subtitle_dict
    finally:
        os.remove(vtt_file_str)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
