from fastapi import FastAPI
import streamlit as st
import os
import yt_dlp
import webvtt
from yt_dlp import YoutubeDL
import pandas as pd

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
    out = []

    for caption in vtt:
        starts.append(caption.start)
        ends.append(caption.end)
        caption_text = caption.text.strip().replace("\n", " ")
        caption_texts.append(caption_text)
        out.append(
            {"start": caption.start, "end": caption.end, "caption_text": caption_text}
        )
    return out


def extract_video_data(url: str):
    tmp_file_str = "tmp"
    ydl_opts = {
        "writesubtitles": True,
        "skip_download": True,
        "outtmpl": tmp_file_str,
        "writeautomaticsub": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_metadata = get_video_metadata(ydl, url)
            if not exist_subtitles(video_metadata):
                raise Exception("No subtitles found")
            ydl.download([url])
        video_title = video_metadata["title"]
        video_description = video_metadata["description"]
        vtt_file_str = tmp_file_str + ".en.vtt"
        subtitle_dict = extract_subtitles_from_vtt(vtt_file_str)
        return {
            "url": url,
            "title": video_title,
            "description": video_description,
            "subtitles": subtitle_dict,
        }
    finally:
        if os.path.exists(vtt_file_str):
            os.remove(vtt_file_str)


def draw_subtitles(subtitle_dict):
    subtitles = subtitle_dict["subtitles"]
    title = subtitle_dict["title"]
    st.write(title)
    if st.toggle("Show Description"):
        st.write(subtitle_dict["description"])
    df = pd.DataFrame(subtitles, columns=["start", "end", "caption_text"])
    st.dataframe(df)
    st.video(subtitle_dict["url"])


def streamlit_app():
    st.title("Generate Notes from Youtube Videos")
    if "video_data" not in st.session_state:
        st.session_state.video_data = {}
    url = st.text_input(
        "Enter the youtube video url",
        placeholder="https://www.youtube.com/watch?v=OkmNXy7er84",
    )
    if st.button("Generate!"):
        st.session_state.video_data = extract_video_data(url)
    if st.session_state.video_data:
        subtitle_dict = st.session_state.data
        draw_subtitles(subtitle_dict)


if __name__ == "__main__":
    streamlit_app()
