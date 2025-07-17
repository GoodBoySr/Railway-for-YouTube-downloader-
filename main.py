from flask import Flask, request, jsonify, send_file from yt_dlp import YoutubeDL import os, uuid, subprocess

app = Flask(name)

@app.route("/api/metadata", methods=["POST"]) def get_metadata(): url = request.json.get("url") if not url: return jsonify({"error": "URL required"}), 400

try:
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title"),
            "duration": info.get("duration"),
            "preview_url": f"https://img.youtube.com/vi/{info['id']}/0.jpg"
        })
except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.route("/api/download", methods=["POST"]) def download_video(): url = request.json.get("url") mode = request.json.get("mode")

if not url or not mode:
    return jsonify({"error": "URL and mode required"}), 400

uid = str(uuid.uuid4())
outdir = f"downloads/{uid}"
os.makedirs(outdir, exist_ok=True)

filepath = os.path.join(outdir, "video.mp4")

ydl_opts = {
    "outtmpl": filepath,
    "format": "bestvideo+bestaudio/best",
    "merge_output_format": "mp4",
    "quiet": True
}

try:
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
        channel = info.get("channel", "unknown")

    trimmed = os.path.join(outdir, "trimmed.mp4")
    mp3_file = os.path.join(outdir, "audio.mp3")

    if mode == "mp3":
        subprocess.run([
            "ffmpeg", "-y", "-i", filepath, "-t", "600", "-q:a", "0", "-map", "a", mp3_file
        ])
        return send_file(mp3_file, as_attachment=True, download_name=f"{title}.mp3")

    elif mode == "with_credit":
        subprocess.run([
            "ffmpeg", "-y", "-i", filepath,
            "-vf", f"drawtext=text='@{channel}':fontcolor=white:fontsize=24:x=w-tw-10:y=10",
            "-codec:a", "copy", trimmed
        ])
        return send_file(trimmed, as_attachment=True, download_name=f"{title}_credit.mp4")

    else:  # no_credit
        subprocess.run(["ffmpeg", "-y", "-i", filepath, "-t", "600", trimmed])
        return send_file(trimmed, as_attachment=True, download_name=f"{title}_short.mp4")

except Exception as e:
    return jsonify({"error": str(e)}), 500

if name == 'main': app.run(debug=True, host="0.0.0.0", port=5000)
