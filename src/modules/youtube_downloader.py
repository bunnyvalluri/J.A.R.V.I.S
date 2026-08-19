"""
youtube_downloader.py — YouTube Media Fetcher
"""

import os
from pathlib import Path


def download_youtube_video(url: str, output_path: str = None) -> str:
    try:
        from pytube import YouTube
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        out_dir = output_path or str(Path.home() / "Downloads")
        video.download(out_dir)
        return f"Downloaded '{yt.title}' to {out_dir}."
    except Exception as e:
        return f"Download failed: {e}"
