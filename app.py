import os
import shutil
import tempfile
from glob import glob

from flask import (Flask, Response, flash, redirect, render_template,
                   request, stream_with_context, url_for)
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-secret"

DOWNLOAD_EXTENSIONS = ["*.mp4", "*.mkv", "*.webm", "*.mp3"]


def find_downloaded_file(directory):
    for pattern in DOWNLOAD_EXTENSIONS:
        files = glob(os.path.join(directory, pattern))
        if files:
            return files[0]
    return None


def stream_file(path, download_name, temp_dir):
    def generate():
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                yield chunk
        try:
            os.remove(path)
        except OSError:
            pass
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except OSError:
            pass

    headers = {
        "Content-Disposition": f"attachment; filename=\"{download_name}\""
    }
    return Response(stream_with_context(generate()), headers=headers, mimetype="application/octet-stream")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("video_url", "").strip()
        output_format = request.form.get("output_format", "mp4")

        if not video_url:
            flash("Please enter a YouTube video URL.", "error")
            return redirect(url_for("index"))

        temp_dir = tempfile.mkdtemp(prefix="ytdownload-")
        try:
            ydl_opts = {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": "bestaudio+bestaudio/best" if output_format == "mp3" else "bestvideo+bestaudio/best",
                "noplaylist": True,
                "quiet": True,
                "ignoreerrors": False,
                "restrictfilenames": True,
            }

            if output_format == "mp3":
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
                ydl_opts["format"] = "bestaudio/best"

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)

            downloaded_file = find_downloaded_file(temp_dir)
            if not downloaded_file:
                flash("Could not find the downloaded file. Try a different video URL.", "error")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return redirect(url_for("index"))

            filename = os.path.basename(downloaded_file)
            return stream_file(downloaded_file, filename, temp_dir)
        except Exception as exc:
            flash(f"Download failed: {exc}", "error")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
