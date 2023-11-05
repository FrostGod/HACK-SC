from fastapi import FastAPI
import streamlit as st
import os
import yt_dlp
import webvtt
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import pandas as pd

app = FastAPI()


@app.get("/")
def home():
    return {"Data: Test"}


def get_video_metadata(ydl: YoutubeDL, url: str):
    info_dict = ydl.extract_info(url, download=False)
    return info_dict


def exist_subtitles(info_dict):
    subtitles = info_dict["subtitles"]
    automatic_captions = info_dict["automatic_captions"]
    return subtitles or automatic_captions


def extract_subtitles_from_vtt(vtt_file_str):
    vtt = webvtt.read(vtt_file_str)
    out = []

    counter = 10
    for caption in vtt:
        caption_text = caption.text.strip().split("\n")[0]
        if out and out[-1]["caption_text"] in caption_text:
            if counter:
                print(f"{caption_text=}")
                counter -= 1
            # replace the previous caption with the current one
            out[-1]["caption_text"] = caption_text
            out[-1]["end"] = caption.end
            continue
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
    vtt_file_str = ""
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
    except DownloadError:
        st.error("Invalid Youtube URL")
        return {}
    finally:
        if os.path.exists(vtt_file_str):
            os.remove(vtt_file_str)


MOCK_VIDEO_DATA = {
    "url": "https://www.youtube.com/watch?v=OkmNXy7er84",
}
MOCK_DATA = [
    [
        "Introduction to the Putnam competition",
        0,
        13,
        "An introduction to the Putnam competition, a challenging math competition for undergraduate students with 12 questions.",
    ],
    [
        "The Challenging Problem",
        72,
        96,
        "The main problem discussed in the video is introduced - 'If you choose four random points on a sphere and consider the tetrahedron with these points as its vertices, what is the probability that the center of the sphere is inside that tetrahedron?'",
    ],
    [
        "Two-Dimensional Case",
        114,
        135,
        "Simplifying the problem by considering a two-dimensional case where three random points are chosen on a circle.",
    ],
    [
        "Probability in Two Dimensions",
        179,
        224,
        "Explaining the probability calculation in two dimensions, where the average probability that the triangle contains the center of the circle is determined.",
    ],
    [
        "Extension to Three Dimensions",
        266,
        283,
        "Extending the problem to three dimensions and explaining how to calculate the probability for the tetrahedron containing the center of the sphere.",
    ],
    [
        "Elegant Insight",
        345,
        383,
        "Discussing the elegant insight of reframing the problem and thinking about choosing lines and points instead of random points.",
    ],
    [
        "General Problem-Solving Approach",
        391,
        435,
        "Providing a general problem-solving approach by breaking down complex problems into simpler cases and looking for key insights.",
    ],
    [
        "Sponsor Message - Brilliant.org",
        575,
        621,
        "Promoting Brilliant.org as a platform for enhancing problem-solving skills and presenting a probability puzzle related to cheating students.",
    ],
    ["Conclusion", 668, 671, "Concluding remarks and closing the video."],
]

MOCK_COLUMNS = ["Title", "Start", "End", "Text"]
MOCK_DF = pd.DataFrame(MOCK_DATA, columns=MOCK_COLUMNS)


def extract_video_id(url: str):
    return url.split("=")[-1]


def video(video_data: dict):
    title = video_data["title"]
    st.video(video_data["url"])
    st.subheader(title)
    with st.expander("Description"):
        st.write(video_data["description"])


def subtitles(video_data: dict):
    subtitles = video_data["subtitles"]
    df = pd.DataFrame(subtitles, columns=["start", "end", "caption_text"])
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={"caption_text": {"width": 600}},
    )


def notes(notes_df: pd.DataFrame, video_data: dict):
    for i, row in notes_df.iterrows():
        if i != 0:
            st.divider()
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(row["Title"])
            st.write(row["Text"])
        with col2:
            video_id = extract_video_id(video_data["url"])
            st.video(video_data["url"], start_time=row["Start"])


def header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Generate Notes from Youtube Videos")
        if "video_data" not in st.session_state:
            st.session_state.video_data = {}
        url = st.text_input(
            "Enter the youtube video url",
            placeholder="https://www.youtube.com/watch?v=OkmNXy7er84",
        )
        if st.button("Generate!"):
            with st.spinner("Generating notes..."):
                video_data = extract_video_data(url)
                if video_data:
                    st.session_state.video_data = video_data


def body():
    if st.session_state.video_data:
        video_data = st.session_state.video_data
        col1, col2 = st.columns([1, 2])
        with col1:
            video(video_data)
        with col2:
            tab1, tab2, tab3 = st.tabs(["Transcript", "Notes", "Mindmap"])
            with tab1:
                subtitles(video_data)
            with tab2:
                notes(MOCK_DF, MOCK_VIDEO_DATA)
            with tab3:
                st.write("Mindmap")


def streamlit_app():
    st.set_page_config(layout="wide")
    header()
    body()


if __name__ == "__main__":
    streamlit_app()
