# youtube-pytubefix-downloader-converter

## New streamlit app

The new streamlit app:
- downloads Youtube videos 
- and extracts subtitles from the videos.

Clone or download this repository to your local machine and navigate to the directory where the `ytapp.py` file is located:
- cd .../youtube-pytubefix-downloader-converter

Create a virtual environment and activate it:
- python -m venv env  # create a virtual environment
- env/Scripts/activate  # activate environment on Windows
- source env/bin/activate  # activate environment on Linux or MacOS.

To run this app locally, you need to install `streamlit` and `yt-dlp`, you may also need `ffmpeg` and some other dependencies installed on your machine:
- pip install streamlit
- pip install yt-dlp

To run the app, type the following command in your terminal or command prompt:
- cd .../youtube-pytubefix-downloader-converter # navigate to the directory where ytapp.py is located
- env/Scripts/activate  # activate environment on Windows
- source env/bin/activate  # activate environment on Linux or MacOS
- streamlit run ytapp.py # run the app

## Old streamlit app

The old streamlit app is not maintained anymore, but could: 
- download Youtube videos, 
- download playlists of Youtube videos, 
- convert videos to mp3 audio, 
- and extract subtitles from the videos.

To run the old app locally, you need to create a conda environment or a virtual environment and install `streamlit` and `pytubefix`, you may also need `ffmpeg` and some other dependencies installed on your machine:
- pip install streamlit
- pip install pytubefix

After that, you can run the app by typing:
- cd .../youtube-pytubefix-downloader-converter
- streamlit run ytapp.py
