import streamlit as st
from pytubefix import YouTube, Playlist
from pathlib import Path
import os

st.title("YouTube Downloader - Video, Audio, and Playlists")

# Initialize session state variables
if 'yt' not in st.session_state:
    st.session_state['yt'] = None
    st.session_state['pl'] = None
    st.session_state['streams'] = []
    st.session_state['captions'] = []
    st.session_state['selected_resolution'] = None

# User inputs the YouTube URL
url = st.text_input("Enter YouTube Video or Playlist URL")

# Determine if the URL is a playlist or a single video
def is_playlist(url):
    return 'playlist' in url

# Fetch video or playlist information
if st.button("Fetch Info"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        try:
            if is_playlist(url):
                # Handle playlist URL
                pl = Playlist(url)
                st.session_state['pl'] = pl
                st.write(f"**Playlist Title:** {pl.title}")
                st.write(f"**Number of Videos:** {len(pl.video_urls)}")
            else:
                # Handle single video URL
                yt = YouTube(url)
                st.session_state['yt'] = yt
                st.write(f"**Title:** {yt.title}")
                st.image(yt.thumbnail_url)
                
                # Get available video streams
                streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
                st.session_state['streams'] = streams
                resolutions = [stream.resolution for stream in streams]
                st.session_state['selected_resolution'] = resolutions[-1]  # Default to highest resolution
    
                # Get available captions
                captions = yt.captions
                caption_list = []
                for caption in captions:
                    caption_list.append(f"{caption.code} - {caption.name}")
                st.session_state['captions'] = caption_list
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Select format and resolution, then download
if st.session_state['yt'] or st.session_state['pl']:
    # Format selection
    format_option = st.radio("Select Download Option", ("Video", "MP3 Audio"))

    # For single video
    if st.session_state['yt'] and not st.session_state['pl']:
        yt = st.session_state['yt']
        streams = st.session_state['streams']
        resolutions = [stream.resolution for stream in streams]
        captions = st.session_state['captions']

        if format_option == "Video":
            # Resolution selection
            selected_resolution = st.selectbox("Select Resolution", resolutions, index=len(resolutions)-1)
            st.session_state['selected_resolution'] = selected_resolution
            subtitle_option = st.checkbox("Download Subtitles with Video (if available)")
            if subtitle_option:
                if captions:
                    selected_video_caption = st.selectbox("Select Subtitle Language for Video", captions)
                    st.session_state['selected_video_caption'] = selected_video_caption
                else:
                    st.error("No subtitles available for this video.")
        else:
            st.session_state['selected_resolution'] = None  # Not needed for audio

    # For playlist
    elif st.session_state['pl'] and not st.session_state['yt']:
        pl = st.session_state['pl']
        st.write(f"Downloading from playlist: {pl.title}")
        # Playlist options
        if format_option == "Video":
            # Resolution selection
            resolution_options = ["Highest Resolution", "Lowest Resolution"]
            selected_resolution_option = st.selectbox("Select Resolution Option", resolution_options)
            st.session_state['selected_resolution_option'] = selected_resolution_option
        # No subtitle options for playlists in this implementation

    # Download button
    if st.button("Download"):
        try:
            download_folder = str(Path.home() / "Downloads")
            if st.session_state['yt'] and not st.session_state['pl']:
                yt = st.session_state['yt']

                # Create a progress bar
                progress_bar = st.progress(0)

                # Progress callback function
                def on_progress(stream, chunk, bytes_remaining):
                    total_size = stream.filesize
                    bytes_downloaded = total_size - bytes_remaining
                    percentage_of_completion = bytes_downloaded / total_size * 100
                    progress_bar.progress(int(percentage_of_completion))

                yt.register_on_progress_callback(on_progress)

                if format_option == "Video":
                    # Filter the stream based on selected resolution
                    ys = yt.streams.filter(resolution=st.session_state['selected_resolution'], progressive=True, file_extension='mp4').first()
                    file_path = ys.download(output_path=download_folder)
                    st.success(f"Video download completed! File saved to {download_folder}")

                    # Download subtitles if checkbox is selected
                    if 'subtitle_option' in locals() and subtitle_option and captions:
                        if 'selected_video_caption' in st.session_state:
                            caption_info = st.session_state['selected_video_caption']
                            caption_code = caption_info.split(' - ')[0]
                            try:
                                caption = yt.captions[caption_code]
                                srt_captions = caption.generate_srt_captions()
                                subtitle_file = os.path.splitext(file_path)[0] + f"_{caption_code}.srt"
                                with open(subtitle_file, 'w', encoding='utf-8') as f:
                                    f.write(srt_captions)
                                st.success(f"Subtitles downloaded and saved to {subtitle_file}")
                            except KeyError:
                                st.error("Selected subtitle not found.")
                        else:
                            st.error("Please select a subtitle language.")
                    elif 'subtitle_option' in locals() and subtitle_option:
                        st.warning("No subtitles available to download.")
                elif format_option == "MP3 Audio":
                    # Download audio stream as MP3
                    ys = yt.streams.get_audio_only()
                    ys.download(output_path=download_folder, mp3=True)
                    st.success(f"MP3 download completed! File saved to {download_folder}")
            elif st.session_state['pl'] and not st.session_state['yt']:
                pl = st.session_state['pl']
                num_videos = len(pl.video_urls)
                progress_bar = st.progress(0)
                current_video = 0

                for video in pl.videos:
                    current_video += 1
                    yt = video

                    # Progress callback function
                    def on_progress(stream, chunk, bytes_remaining):
                        total_size = stream.filesize
                        bytes_downloaded = total_size - bytes_remaining
                        percentage_of_completion = bytes_downloaded / total_size * 100
                        overall_progress = ((current_video - 1) + percentage_of_completion / 100) / num_videos
                        progress_bar.progress(overall_progress)

                    yt.register_on_progress_callback(on_progress)

                    if format_option == "Video":
                        if st.session_state['selected_resolution_option'] == "Highest Resolution":
                            ys = yt.streams.get_highest_resolution()
                        else:
                            ys = yt.streams.get_lowest_resolution()
                        ys.download(output_path=download_folder)
                    elif format_option == "MP3 Audio":
                        ys = yt.streams.get_audio_only()
                        ys.download(output_path=download_folder, mp3=True)
                st.success(f"Playlist download completed! Files saved to {download_folder}")
        except Exception as e:
            st.error(f"An error occurred during download: {e}")
