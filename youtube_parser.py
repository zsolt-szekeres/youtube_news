import yt_dlp
import config
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode

def get_video(url, format='mp3', download=True):

    ytdl_opts = {
    'format': 'bestaudio',
    'outtmpl': 'videos/%(title)s/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': format,
        'preferredquality': '192',
    }],
    'forceduration':True,
    'forcethumbnail': True,
    'writethumbnail': True
    }
    
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info_dict = ytdl.extract_info(url, download=download)
        audio_filename = ytdl.prepare_filename(info_dict)

    return (audio_filename[:-5],format, info_dict)

def is_recent(date_string):
    """
        This decides whether a video is recent based on its publish date 
        compared to today's date and the config parameter for recency.
    """
    date = datetime.strptime(date_string, '%Y%m%d')
    time_difference = datetime.now() - date
    time_limit = timedelta(days=config.params['lookback_days'])
    return (time_difference < time_limit)

def get_videos_from_channel (channel_id, max_results=10): 
    """
        This function gets a list of video IDs from a YouTube channel 
        order by publish date descending and filters out older videos.
    """
    
    url_params = {
        "part": "snippet",    
        "channelId": channel_id,    
        "key": config.params['auth_codes']['Youtube_API_key'],
        "order": "date",
        "maxResults": max_results,
        "type": "video"
    }
    req_url = f"https://www.googleapis.com/youtube/v3/search?{urlencode(url_params)}"
    data = requests.get(req_url).json()
    video_ids = [item["id"]["videoId"] for item in data["items"]]
    return video_ids
