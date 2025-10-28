import streamlit as st
from pathlib import Path
import subprocess
import os
import re
from urllib.parse import urlparse, parse_qs

def extract_youtube_video_id(link: str) -> str:
    try:
        parsed = urlparse(link)
        if not parsed.hostname:
            return None
        host = parsed.hostname.lower()
        if host.endswith('youtu.be'):
            return parsed.path.lstrip('/') or None
        if 'youtube' in host:
            query = parse_qs(parsed.query)
            if 'v' in query:
                return query['v'][0]
            segments = [part for part in parsed.path.split('/') if part]
            if segments:
                if segments[0] == 'shorts' and len(segments) > 1:
                    return segments[1]
                if segments[0] == 'live' and len(segments) > 1:
                    return segments[1]
        return None
    except Exception:
        return None

def build_thumbnail_url(video_id: str) -> str:
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
st.title("YouTube Downloader - Video, Audio, and Playlists")

# Initialize session state variables
if 'info' not in st.session_state:
    st.session_state['info'] = None
    st.session_state['is_playlist'] = False
if 'thumbnail_url' not in st.session_state:
    st.session_state['thumbnail_url'] = None

# User inputs the YouTube URL
url = st.text_input("Enter YouTube Video or Playlist URL")

# Show basic info
if st.button("Fetch Info"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
        st.session_state['thumbnail_url'] = None
    else:
        st.session_state['info'] = url
        st.session_state['is_playlist'] = 'playlist' in url.lower()
        video_id = extract_youtube_video_id(url)
        st.session_state['thumbnail_url'] = build_thumbnail_url(video_id)
        st.success("URL captured. Ready for download.")

# Download section
if st.session_state['info']:
    url = st.session_state['info']
    format_option = st.radio("Select Download Option", ("Video", "MP3 Audio"))
    thumbnail_url = st.session_state.get('thumbnail_url')
    if thumbnail_url:
        st.image(thumbnail_url, caption="Video preview", use_container_width=True)
    elif st.session_state.get('is_playlist'):
        st.info("Preview not available for playlists.")


    resolution = st.selectbox("Select Quality", ["best", "worst"], index=0)
    subtitle_option = st.checkbox("Download Subtitles (if available)", value=False)

    if st.button("Download"):
        download_path = str(Path.home() / "Downloads")
        format_selector = (
            f"{resolution}+bestaudio/best" if format_option == "Video" else "bestaudio/best"
        )
        command = [
            "yt-dlp",
            "-f",
            format_selector,
            "-o",
            os.path.join(download_path, "%(title)s.%(ext)s")
        ]
        format_index = command.index("-f") + 1
        subtitle_args = []
        requested_subtitle_langs = []

        if format_option == "Video":
            command += [
                "--merge-output-format",
                "mp4"
            ]
        else:
            command += [
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "192K"
            ]

        if subtitle_option:
            requested_subtitle_langs = ["en.*", "de", "es", "sl"]
            subtitle_args = [
                "--write-sub",
                "--write-auto-sub",
                "--sub-langs",
                ",".join(requested_subtitle_langs),
                "--sub-format",
                "srt"
            ]

        full_command = command + subtitle_args + [url]

        st.text("Running yt-dlp...")
        result = subprocess.run(full_command, capture_output=True, text=True, shell=True)

        if subtitle_option and result.returncode != 0:
            stderr_text = result.stderr or ""
            stderr_lower = stderr_text.lower()
            subtitle_errors = (
                "no subtitles",
                "subtitles are not available",
                "requested languages",
                "could not download subtitles",
                "unable to download video subtitles",
                "no automatic captions",
                "impersonation",
                "http error 429",
                "too many requests",
                "rate limit"
            )

            if subtitle_args:
                failed_langs = set(
                    match.lower()
                    for match in re.findall(
                        r"unable to download video subtitles for '([^']+)'",
                        stderr_text,
                        flags=re.IGNORECASE
                    )
                )

                if failed_langs and requested_subtitle_langs:
                    def _lang_matches(requested, failed):
                        requested_lower = requested.lower()
                        if requested_lower.endswith('.*'):
                            return failed.startswith(requested_lower[:-2])
                        return requested_lower == failed

                    remaining_langs = [
                        lang for lang in requested_subtitle_langs
                        if not any(_lang_matches(lang, failed) for failed in failed_langs)
                    ]

                    if remaining_langs and len(remaining_langs) < len(requested_subtitle_langs):
                        st.warning(
                            "Skipping unavailable subtitles for: "
                            + ", ".join(sorted(failed_langs))
                            + ". Retrying with available languages."
                        )
                        retry_command = command + [
                            "--write-sub",
                            "--write-auto-sub",
                            "--sub-langs",
                            ",".join(remaining_langs),
                            "--sub-format",
                            "srt",
                            url
                        ]
                        result = subprocess.run(retry_command, capture_output=True, text=True, shell=True)
                        requested_subtitle_langs = remaining_langs
                        subtitle_args = [
                            "--write-sub",
                            "--write-auto-sub",
                            "--sub-langs",
                            ",".join(requested_subtitle_langs),
                            "--sub-format",
                            "srt"
                        ]
                        stderr_text = result.stderr or ""
                        stderr_lower = stderr_text.lower()

            if result.returncode != 0 and any(message in stderr_lower for message in subtitle_errors):
                st.warning("Selected subtitles are not available. Downloading without subtitles.")
                no_subs_command = command + [url]
                result = subprocess.run(no_subs_command, capture_output=True, text=True, shell=True)

        if format_option == "MP3 Audio" and result.returncode != 0:
            audio_error_text = (result.stderr or "").lower()
            audio_403_markers = (
                "http error 403",
                "forbidden",
                "missing a url",
                "requested format is not available",
                "sabr streaming"
            )
            if any(marker in audio_error_text for marker in audio_403_markers):
                fallback_attempts = [
                    ("YouTube android client profile", "youtube:player_client=android"),
                    ("YouTube web client profile", "youtube:player_client=web"),
                    ("YouTube web creator client profile", "youtube:player_client=web_creator"),
                    (
                        "YouTube android client profile with SABR disabled",
                        "youtube:player_client=android,skip=sabr"
                    ),
                    ("SABR disabled", "youtube:skip=sabr")
                ]
                for label, extractor_arg in fallback_attempts:
                    st.warning(
                        "Encountered HTTP 403 when downloading audio. Retrying with "
                        + label
                        + "."
                    )
                    audio_retry_command = command + subtitle_args + [
                        "--extractor-args",
                        extractor_arg,
                        url
                    ]
                    result = subprocess.run(audio_retry_command, capture_output=True, text=True, shell=True)
                    audio_error_text = (result.stderr or "").lower()
                    if result.returncode == 0 or not any(marker in audio_error_text for marker in audio_403_markers):
                        break

                progressive_fallback_format = "best[ext=mp4][height<=720]/best"
                if (
                    result.returncode != 0
                    and any(marker in audio_error_text for marker in audio_403_markers)
                ):
                    st.warning(
                        "Audio-only formats failed. Downloading video stream and extracting audio instead."
                    )
                    video_fallback_command = command.copy()
                    video_fallback_command[format_index] = progressive_fallback_format
                    full_video_command = video_fallback_command + subtitle_args + [url]
                    result = subprocess.run(full_video_command, capture_output=True, text=True, shell=True)
                    audio_error_text = (result.stderr or "").lower()

        if result.returncode == 0:
            st.success("Download completed! Check your Downloads folder.")
        else:
            st.error(f"An error occurred during download:\n{result.stderr}")




















