import yt_dlp
import config
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode

def my_hook(d):
    # if d['status'] == 'downloading':
    #     print ("downloading "+ str(round(float(d['downloaded_bytes'])/float(d['total_bytes'])*100,1))+"%")
    if d['status'] == 'finished':
        print(' - ',d['info_dict']['title'],d['info_dict']['upload_date'])
        #filename=d['filename']
        #rint(filename)
    
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
    'writethumbnail': True,
    'quiet': True,
    'progress_hooks': [my_hook]
    }
    
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info_dict = ytdl.extract_info(url, download=download)
        audio_filename = ytdl.prepare_filename(info_dict)

    return (audio_filename[:-5],format, info_dict)

def is_recent(date_string, lookback=config.params['lookback_days']):
    """
        This decides whether a video is recent based on its publish date 
        compared to today's date and the config parameter for recency.
    """
    date = datetime.strptime(date_string, '%Y%m%d')
    time_difference = datetime.now() - date
    time_limit = timedelta(days=lookback)
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
    response = requests.get(req_url).json()
    video_ids = [item["id"]["videoId"] for item in response["items"]]

    # Deal with the maxResults=50 limit of the Youtube API
    while (('nextPageToken' in response) & (len(video_ids)<max_results)):
        url_params = {
        "part": "snippet",    
        "channelId": channel_id,    
        "key": config.params['auth_codes']['Youtube_API_key'],
        "order": "date",
        "maxResults": max_results-len(video_ids),
        "pageToken":response['nextPageToken'],
        "type": "video"
            }
        req_url = f"https://www.googleapis.com/youtube/v3/search?{urlencode(url_params)}"
        response = requests.get(req_url).json()
        video_ids += [item["id"]["videoId"] for item in response["items"]]
        
    return video_ids
