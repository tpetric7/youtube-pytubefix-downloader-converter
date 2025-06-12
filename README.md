# youtube-pytubefix-downloader-converter

## New streamlit app
The new streamlit app:
- downloads Youtube videos 
- and extracts subtitles from the videos.

To run this app locally, you need to install `streamlit` and `yt-dlp`, you may also need `ffmpeg` and some other dependencies installed on your machine:
- pip install streamlit
- pip install yt-dlp

After that, you can run the app by typing:
- cd .../youtube-pytubefix-downloader-converter
- python -m venv env  # create a virtual environment
- env/Scripts/activate  # activate environment on Windows
- source env/bin/activate  # activate environment on Linux or MacOS
- streamlit run ytapp.py

## Old streamlit app

The old streamlit app is not maintained anymore, but could: 
- downloads Youtube videos, 
- downloads playlists of Youtube videos, 
- converts videos to mp3 audio, 
- and extracts subtitles from the videos.

To run the old app locally, you need to create a conda environment or a virtual environment and install `streamlit` and `pytubefix`, you may also need `ffmpeg` and some other dependencies installed on your machine:
- pip install streamlit
- pip install pytubefix

After that, you can run the app by typing:
- cd .../youtube-pytubefix-downloader-converter
- streamlit run ytapp.py
