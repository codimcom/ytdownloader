import os
import logging

import requests
from moviepy import VideoFileClip
from yt_dlp import YoutubeDL, utils as yt_dlp_utils

logging.basicConfig(level=logging.INFO, filename="downloader.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def download_video(link: str, timestamp: str):
    try:
        # Скачивание видео
        #yt = YouTube(link)
        #if start >= 3:
        #    start_1 = start - 3
        #else:
        #    start_1 = 0
        #duration = end - start_1
        #video_stream = yt.streams.filter(progressive=True, file_extension="mp4", res="360p").first().itag
        # команда для скачивания видео через ffmpeg
        #command = f'ffmpeg -ss {start_1} -i "$(yt-dlp -f {video_stream}/best -g {link})" -t {duration} -c copy videos/output.mp4'
        # Выполняем команду в терминале
        #os.system(command)
        ydl_opts = {
            'download_sections': ['*' + timestamp],
            'outtmpl': 'videos/output.%(ext)s',
            'format': 'bv*[height<=360]+ba/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        print("успешно")
    except Exception as err:
        print(err)
        logging.error(err)


def is_available(link: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # достаточно "плоской" инфы, полный разбор форматов не нужен
        'extract_flat': False,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)

        title = info.get('title')
        author = info.get('uploader') or info.get('channel')
        # берём самое крупное превью
        preview_link = info.get('thumbnail')
        if not preview_link and info.get('thumbnails'):
            preview_link = info['thumbnails'][-1].get('url')

        if title:
            return title, author, preview_link
        return None, None, None
    except yt_dlp_utils.DownloadError as e:
        # видео недоступно / приватное / удалено / регион-лок и т.п.
        logging.error(e)
        return None, None, None
    except Exception as e:
        logging.error(e)
        return None, None, None


def download_preview(link: str, chat_id: int):
    try:
        preview_link = link
        response = requests.get(preview_link)
        print("ready")
        with open(f"preview-{chat_id}.jpg", "wb") as file:
            file.write(response.content)
        return True
    except Exception as e:
        print(e)


def cut(start: int, end: int, video='videos/output.mp4'):
    print(start, end)
    with VideoFileClip('videos/output.mp4') as video:
        new = video.subclipped(start, end)
        new.write_videofile('videos/output_cut.mp4', audio_codec='aac')
    os.remove(video)
    os.rename("videos/output_cut.mp4", video)