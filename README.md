# ytdownload

A simple Flask-based website to download YouTube videos and audio using `yt-dlp`.

## Features

- Download YouTube videos as `MP4`
- Convert YouTube audio to `MP3`
- Simple browser UI

## Setup

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open the site in your browser:

```text
http://127.0.0.1:5000
```

## Notes

- `yt-dlp` is used to fetch the video/audio.
- `ffmpeg` is required for MP3 conversion.
- This project is intended for local use and experimentation.
