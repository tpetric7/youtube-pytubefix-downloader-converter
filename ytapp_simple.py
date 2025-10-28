import streamlit as st
from pathlib import Path
import subprocess
import os

st.title("YouTube Downloader - Video, Audio, and Playlists")

# Initialize session state variables
if 'info' not in st.session_state:
    st.session_state['info'] = None
    st.session_state['is_playlist'] = False

# User inputs the YouTube URL
url = st.text_input("Enter YouTube Video or Playlist URL")

# Show basic info
if st.button("Fetch Info"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        st.session_state['info'] = url
        st.session_state['is_playlist'] = 'playlist' in url.lower()
        st.success("URL captured. Ready for download.")

# Download section
if st.session_state['info']:
    url = st.session_state['info']
    format_option = st.radio("Select Download Option", ("Video", "MP3 Audio"))

    resolution = st.selectbox("Select Quality", ["best", "worst"], index=0)
    subtitle_option = st.checkbox("Download Subtitles (if available)", value=False)

    if st.button("Download"):
        download_path = str(Path.home() / "Downloads")
        command = [
            "yt-dlp",
            "-f", f"{resolution}+bestaudio/best" if format_option == "Video" else "bestaudio",
            "--merge-output-format", "mp4",
            "-o", os.path.join(download_path, "%(title)s.%(ext)s")
        ]

        if format_option == "MP3 Audio":
            command += [
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "192K"
            ]

        if subtitle_option:
            command += ["--write-sub", "--write-auto-sub", "--sub-langs", "en.*,de,es,sl", "--sub-format", "srt"]

        command.append(url)

        st.text("Running yt-dlp...")
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            st.success("Download completed! Check your Downloads folder.")
        else:
            st.error(f"An error occurred during download:\n{result.stderr}")
