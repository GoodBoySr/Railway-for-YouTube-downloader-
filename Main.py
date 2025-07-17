from flask import Flask, request, send_file, jsonify
from pytube import YouTube
import yt_dlp
import subprocess
import os
import uuid

app = Flask(__name__)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def download_video(url, with_credit=False, mp3=False):
    uid = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOADS_DIR, uid)
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_path}/video.%(ext)s',
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        channel = info.get("channel", "UnknownChannel")
        title = info.get("title", "download")

    input_file = os.path.join(output_path, "video.mp4")
    output_file = os.path.join(output_path, f"output.mp4")
    mp3_file = os.path.join(output_path, f"audio.mp3")

    if mp3:
        # Convert to MP3
        subprocess.run([
            "ffmpeg", "-i", input_file, "-q:a", "0", "-map", "a", mp3_file
        ])
        return mp3_file, f"{title}.mp3"

    if with_credit:
        subprocess.run([
            "ffmpeg", "-i", input_file,
            "-vf", f"drawtext=text='@{channel}':fontcolor=white:fontsize=24:x=w-tw-10:y=10",
            "-codec:a", "copy", output_file
        ])
        return output_file, f"{title}_with_credit.mp4"

    return input_file, f"{title}.mp4"


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.json
    url = data.get("url")
    mode = data.get("mode")  # "mp3", "with_credit", "no_credit"

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        file_path, filename = download_video(url, with_credit=(mode == "with_credit"), mp3=(mode == "mp3"))
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
