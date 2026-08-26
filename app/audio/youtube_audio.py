
import sys
import os
import subprocess
import io
import re
from pydub import AudioSegment
from yt_dlp import YoutubeDL


def normalize_youtube_url(url):
    # people paste all kinds of youtube link formats, so we normalize to the standard one
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url


class YouTubeAudio:
    def __init__(self, sample_rate=44100):
        self.target_sample_rate = sample_rate
        self.video_title = None

        # when packaged with pyinstaller, ffmpeg is bundled inside the app
        if getattr(sys, "frozen", False):
            self.ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg")
        else:
            self.ffmpeg_path = "ffmpeg"

    def fetch(self, youtube_url):
        normalized_url = normalize_youtube_url(youtube_url)

        ydl_options = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "extractaudio": False,
            "audioformat": "best",
        }

        with YoutubeDL(ydl_options) as ydl:
            video_info = ydl.extract_info(normalized_url, download=False)
            self.video_title = video_info.get('title', 'Unknown Song')

            if "url" in video_info:
                audio_url = video_info["url"]
            else:
                formats = video_info.get("formats", [])
                audio_formats = [f for f in formats if f.get("acodec") != "none"]
                audio_url = audio_formats[-1]["url"]

        # pipe the stream through ffmpeg to convert to wav instead of saving to disk
        env = os.environ.copy()
        # some systems have broken ssl certs, this gets around it
        env['CURL_CA_BUNDLE'] = ''

        process = subprocess.Popen(
            [self.ffmpeg_path, "-i", audio_url, "-f", "wav",
             "-ar", str(self.target_sample_rate), "-ac", "2", "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env
        )

        raw_audio = process.stdout.read()
        process.stdout.close()
        process.wait()

        return AudioSegment.from_file(io.BytesIO(raw_audio), format="wav")
