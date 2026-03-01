import re


def is_youtube_link(text: str):
    """
    Проверяет, является ли текст ссылкой на видео YouTube.
    """
    text = text.strip()
    youtube_regex = re.compile(
        r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&\S*)?$"
    )
    return bool(youtube_regex.match(text))

def text_preview(title, author):
    text = f"""
Видео найдено 
*{title}* 
👤: {author}
    
теперь введите время начала и конца отрывка в формате hh:mm:ss-hh:mm:ss
"""
    return text


def time_to_seconds(time: str):
    time = list(map(int, time.split(':')))
    #print(time)
    seconds = time[-1]
    if len(time) >= 2:
        seconds += time[-2]*60
    if len(time) == 3:
        seconds += time[-3]*3600
    #print(seconds)
    return seconds
